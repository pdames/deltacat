import ray
import logging
import pyarrow as pa
from collections import defaultdict
from ray import cloudpickle
from deltacat import logs
from typing import Any, Dict, List
from deltacat.compute.compactor.utils import primary_key_index as pki
from deltacat.compute.compactor.model import pyarrow_write_result as pawr

logger = logs.configure_application_logger(logging.getLogger(__name__))


@ray.remote(num_returns=2)
def rewrite_index(
        s3_bucket: str,
        new_primary_key_index_version_locator: Dict[str, Any],
        object_ids: List[Any],
        max_records_per_index_file: int):

    logger.info(f"Starting rewrite primary key index task...")
    object_refs = [cloudpickle.loads(obj_id_pkl) for obj_id_pkl in object_ids]
    logger.info(f"Getting table groups object refs...")
    table_groups_list = ray.get(object_refs)
    logger.info(f"Got {len(table_groups_list)} table groups object refs...")
    hb_index_to_tables = defaultdict(list)
    for table_groups in table_groups_list:
        for hb_index in range(len(table_groups)):
            table = table_groups[hb_index]
            if table is not None:
                hb_index_to_tables[hb_index].append(table)
    logger.info(f"Running {len(hb_index_to_tables)} rewrite index rounds...")
    pki_stats = []
    for hb_index, tables in hb_index_to_tables.items():
        table = pa.concat_tables(tables)
        hb_pki_stats = pki.write_primary_key_index_files(
            table,
            new_primary_key_index_version_locator,
            s3_bucket,
            hb_index,
            max_records_per_index_file,
        )
        pki_stats.append(hb_pki_stats)
    logger.info(f"Finished rewrite primary key index task...")
    return pawr.union(pki_stats), object_refs