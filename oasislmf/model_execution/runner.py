import multiprocessing

import subprocess

from ..utils.exceptions import OasisException
from ..utils.log import oasis_log
from .bash import genbash
from oasislmf.model_preparation.oed import ALLOCATE_TO_ITEMS_BY_PREVIOUS_LEVEL_ALLOC_ID

@oasis_log()
def run(analysis_settings, number_of_processes=-1, num_reinsurance_iterations=0, 
        ktools_mem_limit=False, set_alloc_rule=ALLOCATE_TO_ITEMS_BY_PREVIOUS_LEVEL_ALLOC_ID, set_alloc_rule_gul=1, fifo_tmp_dir=True, filename='run_ktools.sh'):
    if number_of_processes == -1:
        number_of_processes = multiprocessing.cpu_count()

    genbash(number_of_processes, analysis_settings, num_reinsurance_iterations=num_reinsurance_iterations, fifo_tmp_dir=fifo_tmp_dir, gul_alloc_rule=set_alloc_rule_gul, 
            il_alloc_rule=set_alloc_rule, ri_alloc_rule=3, stderr_guard=True,bash_trace=False,filename=filename,_get_getmodel_cmd=None)
    try:
        subprocess.check_call(['bash', filename])
    except subprocess.CalledProcessError as e:
        raise OasisException('Error running ktools: {}'.format(str(e)))
