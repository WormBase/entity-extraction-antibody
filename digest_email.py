import argparse
import datetime
import logging

from wbtools.db.dbmanager import WBDBManager
from wbtools.lib.email.generic import send_email_with_attachment

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="String matching pipeline for antibody")
    parser.add_argument("-N", "--db-name", metavar="db_name", dest="db_name", type=str)
    parser.add_argument("-U", "--db-user", metavar="db_user", dest="db_user", type=str)
    parser.add_argument("-P", "--db-password", metavar="db_password", dest="db_password", type=str, default="")
    parser.add_argument("-H", "--db-host", metavar="db_host", dest="db_host", type=str)
    parser.add_argument("-o", "--email-host", metavar="email_host", dest="email_host", type=str)
    parser.add_argument("-r", "--email-port", metavar="email_port", dest="email_port", type=int)
    parser.add_argument("-u", "--email-user", metavar="email_user", dest="email_user", type=str)
    parser.add_argument("-p", "--email-password", metavar="email_password", dest="email_password", type=str)
    parser.add_argument("-e", "--email-recipient", metavar="email_recipient", dest="email_recipient", type=str)
    parser.add_argument("-t", "--testing", action="store_true")
    parser.add_argument("-l", "--log-file", metavar="log_file", dest="log_file", type=str, default=None,
                        help="path to log file")
    parser.add_argument("-L", "--log-level", dest="log_level", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR',
                                                                        'CRITICAL'], default="INFO",
                        help="set the logging level")

    args = parser.parse_args()
    logging.basicConfig(filename=args.log_file, level=args.log_level,
                        format='%(asctime)s - %(name)s - %(levelname)s:%(message)s')

    db_manager = WBDBManager(dbname=args.db_name, user=args.db_user, password=args.db_password, host=args.db_host)
    paperid_antibodystr = db_manager.generic.get_antibody_str_values(
        from_date=datetime.datetime.now() - datetime.timedelta(days=7))
    empty_papers = []
    nonempty_papers = []
    for paper_id, antibody_str in paperid_antibodystr:
        if antibody_str:
            nonempty_papers.append((paper_id, antibody_str))
        else:
            empty_papers.append((paper_id, antibody_str))
    email_text = "PAPER_ID&emsp;ANTIBODY_STR_DATA<br/>"
    attachment_text = "PAPER_ID\tANTIBODY_STR_DATA\n"
    cur_status_source = "tazendra" if not args.testing else "mangolassi"
    for paper_id, antibody_str in [*nonempty_papers, *empty_papers]:
        cur_stat_form_link = f"<a href=\"http://{cur_status_source}.caltech.edu/~postgres/cgi-bin/curation_status.cgi?select_cu" \
                             f"rator=two1823&select_datatypesource=caltech&specific_papers={paper_id}&select_t" \
                             f"opic=none&checkbox_antibody=antibody&checkbox_oa=on&checkbox_cur=on&checkbox_svm=on" \
                             f"&checkbox_str=on&checkbox_afp=on&checkbox_cfp=on&papers_per_page=10&checkbox_journal=" \
                             f"on&checkbox_pmid=on&checkbox_pdf=on&action=Get+Results\">{paper_id}</a>"
        email_text += cur_stat_form_link + "&emsp;" + antibody_str + "<br/>"
        attachment_text += paper_id + "\t" + antibody_str + "\n"
    send_email_with_attachment(subject=("[Test] " if args.testing else "") + "[Antibody STR] Weekly Digest",
                               content=email_text, recipients=[args.email_recipient], server_host=args.email_host,
                               server_port=args.email_port, email_user=args.email_user,
                               email_passwd=args.email_password, attachment=attachment_text,
                               attachment_filename="results.tsv")
    logger.info("Finished")


if __name__ == '__main__':
    main()

