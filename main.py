# exclude Ascaris human Drosophila mammalian murine?

import argparse
import itertools
import logging
import re

from wbtools.db.dbmanager import WBDBManager
from wbtools.literature.corpus import CorpusManager


# EXCLUDE_WORDS = ["anti-mouse", "anti-human", "anti-inflammatory", "anti-aging", "anti-phase", "anti-digoxigenin",
# "anti-m1a", "anti-gapdh", "anti-HA", "anti-FLAG", "anti-Flag", "anti-His", "anti-GST", "anti-Xpress", "anti-V5",
# "anti-HPC4", "anti-Myc", "anti-myc", "anti-phophotyrosine", "anti-serotonin", "anti-5HT", "anti-5-HT", "anti-HRP",
# "anti-GABA", "anti-ubiquitin", "anti-GFP", "anti-actin", "anti-FMRFamide", "anti-RFamide", "anti-MBP", "anti-TMG",
# "anti-VSV", "anti-H3K4me3"]

COMBINATION_1 = ["preparation", "prepared", "prepare", "production", "purification", "generation", "generate",
                 "generated", "produce", "produced", "purify", "purified", "raised"]
COMBINATION_2 = ["antiserum", "antibody", "antibodies", "antisera"]


logger = logging.getLogger(__name__)


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
        exclude_ids=already_processed, pap_types=["Journal_article"], exclude_temp_pdf=True)
    logger.info("Finished loading papers from DB")
    combinations = list(itertools.product(COMBINATION_1, COMBINATION_2))
    curated_gene_names = [re.escape(gene_name.lower()) for gene_name in db_manager.generic.get_curated_genes(
        exclude_id_used_as_name=True)]
    anti_gene_regex = re.compile(r"(?i)[\s\(\[\{\.,;:\'\"\<](anti\-(?:" + "|".join(curated_gene_names) +
                                 "|C\. elegans))[\s\.;:,'\"\)\]\}\>\?]")
    combinations_regex = [(comb, re.compile(".*" + comb[0] + "\s.*" + comb[1] + "[\s\.;:,'\"\)\]\}\>\?]"),
                           re.compile(".*" + comb[1] + "\s.*" + comb[0] + "[\s\.;:,'\"\)\]\}\>\?]")) for comb in
                          combinations]
    for paper in cm.get_all_papers():
        logger.info("Extracting antibody info from paper " + paper.paper_id)
        sentences = paper.get_text_docs(include_supplemental=True, split_sentences=True, lowercase=False)
        matches = set()
        for sentence in sentences:
            sentence = sentence.replace('–', '-')
            results = re.findall(anti_gene_regex, sentence)
            matches.update(results)
            matches.update([comb[0] + " " + comb[1] for comb, regex1, regex2 in combinations_regex if
                            re.match(regex1, sentence.lower()) or re.match(regex2, sentence.lower())])
        db_manager.generic.save_antybody_str_values(paper_id=paper.paper_id, str_values=", ".join(matches))
        logger.info("Values for paper " + paper.paper_id + " saved to DB")
    logger.info("Finished")


if __name__ == '__main__':
    main()

