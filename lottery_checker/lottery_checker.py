import argparse
import json
import urllib.request
import smtplib
from datetime import date, timedelta

# This utility will fetch todays results from a web site (this is set up to work with the Mega Millions results)
# The winning numbers are compared to see if you are now a millionaire!
# The results can be emailed to you. Use crontab to ensure this runs on the correct days (1 day after the drawing)
# Author: Colin Turner (koolspin)


def validate_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Path to the config file - contains all the info needed to run")
    args = parser.parse_args()
    if args.input is None:
        print("You must provide a config file", file=sys.stderr)
        return False, None
    else:
        return True, args.input


def load_config(config_path):
    with open(config_path) as js_file:
        js_obj = json.load(js_file)
        config_obj = js_obj["config"]
        base_uri = config_obj["lottery_results_base_uri"]
        our_numbers = config_obj["my_numbers"]
        draw_days = config_obj["draw_days"]
        smtp_conf = None
        if "smtp_config" in config_obj:
            smtp_conf = config_obj["smtp_config"]
        return base_uri, our_numbers, draw_days, smtp_conf


def format_date_parameter(draw_days):
    draw_date = date.today()
    while True:
        weekday = draw_date.weekday()
        if weekday in draw_days:
            date_str = draw_date.isoformat()
            query_str = '{0}T00:00:00.000'.format(date_str)
            return query_str
        else:
            draw_date = draw_date - timedelta(days=1)


def fetch_latest_results(base_uri, param):
    full_uri = '{0}?draw_date={1}'.format(base_uri, param)
    print('full_uri: {0}'.format(full_uri))
    resp = urllib.request.urlopen(full_uri)
    data = resp.read()
    js_str = data.decode('utf-8')
    print('js_str: {0}'.format(js_str))
    js_obj = json.loads(js_str)
    return js_obj


def format_winning_number_array(res_obj):
    win_array = []
    win = res_obj[0]
    nums = win["winning_numbers"].split()
    for num_str in nums:
        num = int(num_str)
        win_array.append(num)
    special_ball = win["mega_ball"]
    win_array.append(int(special_ball))
    return win_array


def compare_winning_numbers(lnums, my_array):
    matchmsg = ""
    mostmatches = 0
    for myset in my_array:
        matchcnt = 0
        matchmsg += "Comparing my set: " + str(myset) + "\r\n"
        matchmsg += "With today's:     " + str(lnums) + "\r\n"
        for i in range(0, 5):
            xx = lnums.count(myset[i])
            if xx > 0:
                ix = lnums.index(myset[i])
                if ix < 5:
                    matchcnt += 1
        if matchcnt > 1:
            matchmsg += "** "
        matchmsg += "Total matches:    " + str(matchcnt) + "\r\n"
        if myset[5] == lnums[5]:
            matchcnt += 1
            matchmsg += "** MB match!\r\n"
        if matchcnt > mostmatches:
            mostmatches = matchcnt
    return mostmatches, matchmsg


def email_results(match_info, smtp_conf):
    smtp_server = smtp_conf["smtp_server"]
    smtp_from = smtp_conf["smtp_from"]
    smtp_to = smtp_conf["smtp_to"]
    server = smtplib.SMTP(smtp_server)
    server.set_debuglevel(0)
    msg = "From: {0}\r\n".format(smtp_from)
    msg += "To: {0}\r\n".format(smtp_to)
    msg += "Subject: Today's numbers ({0})\r\n".format(match_info[0])
    msg += match_info[1]
    server.sendmail(smtp_from, [smtp_to], msg)
    server.quit()


res = validate_args()
if res[0]:
    conf = load_config(res[1])
    param = format_date_parameter(conf[2])
    results_obj = fetch_latest_results(conf[0], param)
    winning_array = format_winning_number_array(results_obj)
    match_info = compare_winning_numbers(winning_array, conf[1])
    print(match_info[0])
    print(match_info[1])
    if conf[3] is not None:
        email_results(match_info, conf[3])
    exit(0)
else:
    exit(1)
