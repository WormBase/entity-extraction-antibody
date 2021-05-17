# exclude Ascaris human Drosophila mammalian murine?

import argparse
import itertools
import logging
import re

from wbtools.lib.email.generic import send_email_with_attachment

from wbtools.db.dbmanager import WBDBManager
from wbtools.lib.nlp.common import PaperSections
from wbtools.literature.corpus import CorpusManager


# EXCLUDE_WORDS = ["anti-mouse", "anti-human", "anti-inflammatory", "anti-aging", "anti-phase", "anti-digoxigenin",
# "anti-m1a", "anti-gapdh", "anti-HA", "anti-FLAG", "anti-Flag", "anti-His", "anti-GST", "anti-Xpress", "anti-V5",
# "anti-HPC4", "anti-Myc", "anti-myc", "anti-phophotyrosine", "anti-serotonin", "anti-5HT", "anti-5-HT", "anti-HRP",
# "anti-GABA", "anti-ubiquitin", "anti-GFP", "anti-actin", "anti-FMRFamide", "anti-RFamide", "anti-MBP", "anti-TMG",
# "anti-VSV", "anti-H3K4me3"]

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

    # TODO: delete
    parser.add_argument("-o", "--email-host", metavar="email_host", dest="email_host", type=str)
    parser.add_argument("-r", "--email-port", metavar="email_port", dest="email_port", type=int)
    parser.add_argument("-u", "--email-user", metavar="email_user", dest="email_user", type=str)
    parser.add_argument("-p", "--email-password", metavar="email_password", dest="email_password", type=str)


    args = parser.parse_args()
    logging.basicConfig(filename=args.log_file, level=args.log_level,
                        format='%(asctime)s - %(name)s - %(levelname)s:%(message)s')

    cm = CorpusManager()
    db_manager = WBDBManager(dbname=args.db_name, user=args.db_user, password=args.db_password, host=args.db_host)
    already_processed = db_manager.antibody.get_paper_ids_processed_antibody()
    cm.load_from_wb_database(
        args.db_name, args.db_user, args.db_password, args.db_host, tazendra_ssh_user=args.tazendra_ssh_user,
        tazendra_ssh_passwd=args.tazendra_ssh_password, from_date=args.from_date, max_num_papers=args.max_num_papers,
        #exclude_ids=already_processed, pap_types=["Journal_article"], exclude_temp_pdf=True)
        pap_types=["Journal_article"], exclude_temp_pdf=True,
        paper_ids=["00059332","00059297","00059440","00059419","00059375","00059351","00059335","00059295","00061090","00061062","00061032","00061187","00061201","00061199","00061190","00061185","00061184","00061178","00061182","00061161","00061148","00061147","00061139","00061137","00061125","00061123","00061115","00061150","00061108","00061106","00058920","00058815","00059269","00059222","00059191","00059187","00059174","00058998","00058976","00058945","00058876","00058869","00058836","00058768","00061081","00061072","00058594","00057340","00057338","00057256","00057347","00057305","00057304","00057208","00057162","00057160","00057146","00057144","00057143","00057142","00057135","00057041","00057040","00057037","00061045","00061038","00059409","00059401","00059339","00059338","00059444","00059443","00059442","00059431","00059428","00059424","00059418","00059417","00059410","00059408","00059398","00059394","00059393","00059382","00059381","00059378","00059376","00059369","00059365","00059359","00059355","00059348","00059347","00059343","00059342","00059340","00059337","00059336","00059333","00059331","00059326","00059325","00059314","00059311","00059309","00059308","00059302","00059292","00059282","00061203","00061202","00061097","00061089","00061080","00061043","00061025","00061024","00061198","00061197","00061177","00061174","00061165","00061127","00061101","00061200","00061196","00061193","00061191","00061188","00061186","00061183","00061180","00061176","00061175","00061173","00061172","00061195","00061192","00061189","00061181","00061179","00061076","00060981","00061171","00061170","00061168","00061167","00061166","00061164","00061162","00061158","00061155","00061154","00061149","00061146","00061138","00061136","00061135","00061134","00061133","00061131","00061130","00061126","00061122","00061121","00061120","00061116","00061114","00061169","00061163","00061159","00061153","00061152","00061151","00061145","00061144","00061143","00061142","00061141","00061140","00061128","00061124","00061119","00061118","00061117","00061112","00061107","00061104","00061103","00061100","00061099","00061098","00059275","00059221","00059160","00059101","00059098","00059079","00058939","00058889","00058883","00058880","00058854","00058822","00058782","00058734","00058721","00058718","00058715","00058684","00058671","00061111","00061110","00061109","00061105","00059274","00059272","00059271","00059265","00059264","00059263","00059261","00059258","00059255","00059251","00059231","00059225","00059224","00059223","00059219","00059217","00059214","00059213","00059203","00059190","00059188","00059186","00059185","00059182","00059178","00059148","00059143","00059134","00059125","00059121","00059118","00059115","00059114","00059113","00059112","00059106","00059099","00059078","00059070","00059061","00059055","00059043","00059038","00059036","00059034","00059032","00059030","00059019","00059018","00059017","00059009","00059001","00058999","00058997","00058994","00058990","00058979","00058974","00058973","00058969","00058968","00058965","00058963","00058962","00058959","00058958","00058957","00058955","00058954","00058953","00058950","00058948","00058946","00058944","00058943","00058941","00058938","00058937","00058933","00058929","00058928","00058925","00058923","00058921","00058919","00058913","00058912","00058910","00058909","00058897","00058891","00058885","00058884","00058878","00058877","00058875","00058874","00058871","00058860","00058856","00058848","00058846","00058844","00058842","00058841","00058840","00058839","00058838","00058837","00058835","00058834","00058825","00058819","00058817","00058816","00058814","00058813","00058805","00058803","00058800","00058799","00058798","00058797","00058793","00058792","00058784","00058783","00058781","00058765","00058753","00058746","00058744","00058741","00058736","00058731","00058725","00058716","00058712","00058711","00058710","00058705","00058700","00058698","00058692","00058682","00058678","00058676","00058670","00058665","00058650","00058649","00058648","00058646","00061096","00061093","00061092","00061091","00061088","00061087","00061086","00061085","00061075","00061074","00061084","00061083","00061082","00061079","00061078","00061077","00061070","00061071","00058615","00058609","00057345","00057337","00057328","00057292","00057287","00057255","00057248","00057205","00057109","00057054","00058617","00058613","00058611","00058607","00058606","00058600","00058587","00058586","00058585","00057353","00057349","00057348","00057346","00057330","00057318","00057306","00057299","00057290","00057286","00057270","00057269","00057267","00057266","00057265","00057258","00057253","00057244","00057243","00057241","00057239","00057223","00057222","00057221","00057220","00057218","00057215","00057209","00057180","00057177","00057176","00057166","00057164","00057156","00057154","00057153","00057150","00057147","00057145","00057141","00057140","00057139","00057137","00057136","00057127","00057126","00057124","00057123","00057122","00057114","00057113","00057112","00057108","00057104","00057099","00057095","00057094","00057089","00057088","00057086","00057067","00057063","00057051","00057039","00057038","00057035","00057034","00057031","00057028","00057027","00057021","00061069","00061067","00061066","00061065","00061061","00061060","00061058","00061057","00061056","00061055","00061053","00061051","00061049","00061048","00061047","00061046","00061042","00061041","00061040","00061039","00061037","00061068"])
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

    # TODO: delete
    email_text = "PAPER_ID&emsp;CSF_VALUE&emsp;ANTIBODY_STR_DATA_FULLTEXT<br/>"
    attachment_text = "PAPER_ID\tCSF_VALUE\tANTIBODY_STR_DATA_FULLTEXT\n"
    results = []

    for paper in cm.get_all_papers():
        logger.info("Extracting antibody info from paper " + paper.paper_id)
        sentences = paper.get_text_docs(include_supplemental=True, split_sentences=True, lowercase=False,
                                        remove_sections=[PaperSections.REFERENCES], must_be_present=[PaperSections.METHOD, PaperSections.RESULTS])
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

        results.append((paper.paper_id, db_manager.antibody.get_antibody_str_value(paper.paper_id),
                        ", ".join(matches)))
        #db_manager.generic.save_antybody_str_values(paper_id=paper.paper_id, str_values=", ".join(matches))
        #logger.info("Values for paper " + paper.paper_id + " saved to DB")

    # TODO: delete
    for paper_id, csf_value, antibody_str in results:
        cur_stat_form_link = f"<a href=\"http://mangolassi.caltech.edu/~postgres/cgi-bin/curation_status.cgi?select_cu" \
        f"rator=two1823&select_datatypesource=caltech&specific_papers={paper_id}&select_t" \
        f"opic=none&checkbox_antibody=antibody&checkbox_oa=on&checkbox_cur=on&checkbox_svm=on" \
        f"&checkbox_str=on&checkbox_afp=on&checkbox_cfp=on&papers_per_page=10&checkbox_journal=" \
        f"on&checkbox_pmid=on&checkbox_pdf=on&action=Get+Results\">{paper_id}</a>"
        email_text += cur_stat_form_link + "&emsp;" + (csf_value if csf_value else "") + "&emsp;" + antibody_str + "<br/>"
        attachment_text += paper_id + "\t" + (csf_value if csf_value else "") + "\t" + antibody_str + "\n"
    send_email_with_attachment(subject="[Test][Antibody STR] Results",
                               content=email_text, recipients=["valearna@caltech.edu"], server_host=args.email_host,
                               server_port=args.email_port, email_user=args.email_user,
                               email_passwd=args.email_password, attachment=attachment_text,
                               attachment_filename="results.tsv")
    logger.info("Finished")


if __name__ == '__main__':
    main()

