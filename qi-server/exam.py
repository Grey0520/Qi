from bs4 import BeautifulSoup

from auth3 import Auth


def exam_handler(cookies, xnxqid, output_dir='.'):
    auth = Auth(cookies)
    url = 'https://jwxt.sztu.edu.cn/jsxsd/xsks/xsksap_list'
    r = auth.post(url, data={'xnxqid': xnxqid})
    print(r.text)

    soup = BeautifulSoup(r.text, features='html.parser')
    tables = soup.findAll('table')
    if len(tables) < 1:
        raise Exception('未查询到考试安排')

    tab = tables[0]
    schedules = []
    for tr in tab.findAll('tr'):
        if tr.findAll('td'):
            exam = tr.findAll('td')
            origDayTimeText = exam[7].getText().split(' ')
            day = origDayTimeText[0]
            origTimeText = origDayTimeText[1].split('~')
            startTime = origTimeText[0]
            endTime = origTimeText[1]
            print(day, startTime, endTime)
            tmp = {
                'name': exam[5].getText(),
                'day': day,
                'startTime': startTime,
                'endTime': endTime,
                'location': exam[8].getText()
            }
            print(tmp)
            schedules.append(tmp)
        print("---------------------------")

    # 创建 ics
    ics = "%s/%s-exam.ics" % (output_dir, xnxqid)
    f = open(ics, 'w', encoding='utf-8')
    f.write(u'BEGIN:VCALENDAR\nVERSION:2.0\n')
    for exam in schedules:
        message = '''
BEGIN:VEVENT
SUMMARY:%s
DTSTART;TZID="UTC+08:00";VALUE=DATE-TIME:%sT%s
DTEND;TZID="UTC+08:00";VALUE=DATE-TIME:%sT%s
LOCATION:%s
END:VEVENT\n''' % (
            exam['name'], exam['day'].replace('-', ''), exam['startTime'].replace(':', '') + "00",
            exam['day'].replace('-', ''),
            exam['endTime'].replace(':', '') + "00", exam['location'])

        print(message)
        f.write(message)

    f.write(u'END:VCALENDAR')
    f.close()

    return ics
