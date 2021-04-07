# exclude Ascaris human Drosophila mammalian murine?

import argparse
import itertools
import logging
import re

from wbtools.db.dbmanager import WBDBManager
from wbtools.literature.corpus import CorpusManager


EXCLUDE_WORDS = ["anti-HA", "anti-FLAG", "anti-Flag", "anti-His", "anti-GST", "anti-Xpress", "anti-V5", "anti-HPC4", "anti-Myc", "anti-myc", "anti-phophotyrosine", "anti-serotonin", "anti-5HT", "anti-5-HT", "anti-HRP", "anti-GABA", "anti-ubiquitin", "anti-GFP", "anti-actin", "anti-FMRFamide", "anti-RFamide", "anti-MBP", "anti-TMG", "anti-VSV", "anti-H3K4me3"]
COMBINATION_1 = ["preparation", "prepared", "prepare", "production", "purification", "generation", "generate", "generated", "produce", "produced", "purify", "purified", "raised"]
COMBINATION_2 = ["antiserum", "antibody", "antibodies", "antisera"]


def main():
    parser = argparse.ArgumentParser(description="String matching pipeline for antibody")
    parser.add_argument("-N", "--db-name", metavar="db_name", dest="db_name", type=str)
    parser.add_argument("-U", "--db-user", metavar="db_user", dest="db_user", type=str)
    parser.add_argument("-P", "--db-password", metavar="db_password", dest="db_password", type=str, default="")
    parser.add_argument("-H", "--db-host", metavar="db_host", dest="db_host", type=str)
    parser.add_argument("-w", "--tazendra-ssh-username", metavar="tazendra_ssh_user", dest="tazendra_ssh_user",
                        type=str)
    parser.add_argument("-z", "--tazendra_ssh_password", metavar="tazendra_ssh_password", dest="tazendra_ssh_password",
                        type=str)
    parser.add_argument("-l", "--log-file", metavar="log_file", dest="log_file", type=str, default=None,
                        help="path to log file")
    parser.add_argument("-L", "--log-level", dest="log_level", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR',
                                                                        'CRITICAL'], default="INFO",
                        help="set the logging level")
    parser.add_argument("-d", "--from-date", metavar="from_date", dest="from_date", type=str,
                        help="use only articles included in WB at or after the specified date")
    parser.add_argument("-m", "--max-num-papers", metavar="max_num_papers", dest="max_num_papers", type=int)

    args = parser.parse_args()
    logging.basicConfig(filename=args.log_file, level=args.log_level,
                        format='%(asctime)s - %(name)s - %(levelname)s:%(message)s')

    cm = CorpusManager()
    db_manager = WBDBManager(dbname=args.db_name, user=args.db_user, password=args.db_password, host=args.db_host)
    already_processed = db_manager.generic.get_paper_ids_processed_antibody()
    cm.load_from_wb_database(
        args.db_name, args.db_user, args.db_password, args.db_host, tazendra_ssh_user=args.tazendra_ssh_user,
        tazendra_ssh_passwd=args.tazendra_ssh_password, from_date=args.from_date, max_num_papers=args.max_num_papers,
        exclude_ids=already_processed, pap_types=["Journal_article"])
    combinations = [pair[0] + " " + pair[1] for pair in itertools.product(COMBINATION_1, COMBINATION_2)]
    for paper in cm.get_all_papers():
        sentences = paper.get_text_docs(include_supplemental=True, split_sentences=True, lowercase=True)
        matches = set()
        for sentence in sentences:
            results = re.findall(r"anti\-[\w]+", sentence)
            matches.update(list(results))
            matches.update([comb for comb in combinations if comb in sentence])
        matches = matches - set([exc.lower() for exc in EXCLUDE_WORDS])
    # TODO: save results to DB
    pass


if __name__ == '__main__':
    main()

