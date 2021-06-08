import argparse
import itertools
import logging
import re

from wbtools.db.dbmanager import WBDBManager
from wbtools.literature.corpus import CorpusManager


EXCLUDE_GENES = ['PDI']
ADDITIONAL_ANTI_KEYWORDS = ['MSP']
ADDITIONAL_KEYWORDS = ['MH46', 'SP56', 'a-SP56']

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
    parser.add_argument("-y", "--ssh-host", metavar="ssh_host", dest="ssh_host",
                        type=str)
    parser.add_argument("-w", "--ssh-username", metavar="ssh_user", dest="ssh_user",
                        type=str)
    parser.add_argument("-z", "--ssh-password", metavar="ssh_password", dest="ssh_password",
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
    already_processed = db_manager.antibody.get_paper_ids_processed_antibody()
    cm.load_from_wb_database(
        args.db_name, args.db_user, args.db_password, args.db_host, ssh_host=args.ssh_host, ssh_user=args.ssh_user,
        ssh_passwd=args.ssh_password, from_date=args.from_date, max_num_papers=args.max_num_papers,
        exclude_ids=already_processed, pap_types=["Journal_article"], exclude_temp_pdf=True)
    logger.info("Finished loading papers from DB")
    combinations = list(itertools.product(COMBINATION_1, COMBINATION_2))
    curated_gene_names = [re.escape(gene_name.lower()) for gene_name in db_manager.generic.get_curated_genes(
        exclude_id_used_as_name=True)]
    curated_gene_names = list(set(curated_gene_names) - set([gene_name.lower() for gene_name in EXCLUDE_GENES]))
    additional_match_regex = re.compile(r"[\s\(\[\{\.,;:\'\"\<](" + "|".join(ADDITIONAL_KEYWORDS) + ")[\s\.;:,'\"\)\]\}\>\?]")
    curated_gene_names.extend([re.escape(additional_gene.lower()) for additional_gene in ADDITIONAL_ANTI_KEYWORDS])
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
            sentence = sentence.replace('‐', '-')

            # match anti-GENE patterns
            anti_gene_matches = re.findall(anti_gene_regex, sentence)
            anti_gene_matches = [anti_gene_match for anti_gene_match in anti_gene_matches if
                                 anti_gene_match[5:].lower() != anti_gene_match[5:]]
            matches.update(anti_gene_matches)

            # match combinations
            comb_matches = [comb[0] + " " + comb[1] for comb, regex1, regex2 in combinations_regex if
                            re.match(regex1, sentence.lower()) or re.match(regex2, sentence.lower())]
            matches.update(comb_matches)

            # additional matches
            add_matched = re.findall(additional_match_regex, sentence)
            matches.update(add_matched)

        db_manager.antibody.save_antybody_str_values(paper_id=paper.paper_id, str_values=", ".join(matches))
        logger.info("Values for paper " + paper.paper_id + " saved to DB")
    logger.info("Finished")


if __name__ == '__main__':
    main()
