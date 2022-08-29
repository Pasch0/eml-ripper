import re
import sys
import random
from multiprocessing import Process
import http.server
import socketserver
import subprocess as sp
from rich.console import Console
from fast_mail_parser import parse_email, ParseError

c = Console()
cprint = c.print

lb = '\n##########################################################################################################################################\n'

try:
    for i in sys.argv:
        if '.eml' in i:
            eml = i
        else:
            pass
    if eml:
        pass
    else:
        cprint('[warning]Qual arquivo deve ser analisado?[/warning]')
        sys.exit(0)
except OSError as e:
    cprint(f'[warning]{e}[/warning]')
    sys.exit(1)

port = lambda: random.randint(4000, 6000)
handler = http.server.SimpleHTTPRequestHandler

usedport = [0]
msg = '\n'
rint = lambda: random.randint(0, 255)
colors = lambda: "#%02x%02x%02x" % (rint(), rint(), rint())
regex = r"\b((?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])))(?::[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?(?:/[\w\.-]*)*/?)\b"
exits = ['quit', 'exit', 'break', 'sair', 'fechar', ':q', ':q!', 'q']
cc, rp, xtm, aut, spf, rspf, mfrom, to, subject, date = None, None, None, None, None, None, None, None, None, None
root = ['Todos os cabeçalhos', 'Mensagem', 'Extrair anexos', 'HTML', 'Exportar HTML', 'Checar reputação do remetente']
headers = {}
html = ''
tags = []
printer = []
attachments = []
body = []
counter = 0
stage = 0
lists = [root, tags]
stages = {0:lists[0], 1:lists[1]}
response = []
hurl = []
murl = []
banner = ''
logoy = '''

████████╗██████╗ ██╗   ██╗    ██████╗ ██╗  ██╗██╗   ██╗███████╗██╗  ██╗    ███╗   ███╗███████╗
╚══██╔══╝██╔══██╗╚██╗ ██╔╝    ██╔══██╗██║  ██║╚██╗ ██╔╝██╔════╝██║  ██║    ████╗ ████║██╔════╝
   ██║   ██████╔╝ ╚████╔╝     ██████╔╝███████║ ╚████╔╝ ███████╗███████║    ██╔████╔██║█████╗  
   ██║   ██╔══██╗  ╚██╔╝      ██╔═══╝ ██╔══██║  ╚██╔╝  ╚════██║██╔══██║    ██║╚██╔╝██║██╔══╝  
   ██║   ██║  ██║   ██║       ██║     ██║  ██║   ██║   ███████║██║  ██║    ██║ ╚═╝ ██║███████╗
   ╚═╝   ╚═╝  ╚═╝   ╚═╝       ╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝    ╚═╝     ╚═╝╚══════╝
                                                                                              
'''

logo = '''

████████╗██████╗ ██╗   ██╗    ██████╗ ██╗  ██╗██╗███████╗██╗  ██╗    ███╗   ███╗███████╗
╚══██╔══╝██╔══██╗╚██╗ ██╔╝    ██╔══██╗██║  ██║██║██╔════╝██║  ██║    ████╗ ████║██╔════╝
   ██║   ██████╔╝ ╚████╔╝     ██████╔╝███████║██║███████╗███████║    ██╔████╔██║█████╗  
   ██║   ██╔══██╗  ╚██╔╝      ██╔═══╝ ██╔══██║██║╚════██║██╔══██║    ██║╚██╔╝██║██╔══╝  
   ██║   ██║  ██║   ██║       ██║     ██║  ██║██║███████║██║  ██║    ██║ ╚═╝ ██║███████╗
   ╚═╝   ╚═╝  ╚═╝   ╚═╝       ╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝    ╚═╝     ╚═╝╚══════╝
                                                                                         
'''


with open(eml, 'r') as f:
    email = f.read()

def cat(target, pattern):
    mailx = []
    if pattern == 'email':
        mails = re.findall('\S.+@.+\S', target)
        for mx in mails:
            if '<' in mx:
                mx = mx.split('<')[1].replace('>', '')
                mailx.append(mx)
            else:
                mailx.append(mx)
    return mailx

def ask():
    ask = input('\n/: ')
    check_input(ask)

def header():
    print(lb)
    for tag in tags:
        print(f'\n{tags.index(tag)}- {tag}')
    print(banner)
    ask()

def hexec(option):
    global stage
    printer.clear()
    printer.append(f'{lb}\n\n{tags[int(option)]}: {headers[tags[int(option)]]}')
    stage = 0

def extract():
    printer.clear()
    mail = parse_email(email)
    for att in mail.attachments:
        if len(att.filename) >= 1:
            with open(f'extract_{att.filename}', 'w+') as f: 
                f.write(att.content.decode())
    printer.append(f'\n\nAnexo {att.filename} salvo como: extract_{att.filename}')

def checkIP():
    ips = re.findall( r'[0-9]+(?:\.[0-9]+){3}', headers['X-TM-Authentication-Results'])
    for ip in ips:
        sp.call(f'python3 badip.py -i {ip}', shell=True)
    input('\n/:')

def http(port):
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

def check_input(input):
    global stage, https
    if input == '00':
        printer.clear()
    elif input == 'clear':
        printer.clear()
        print('\033c')
    elif input in exits:
        sys.exit(0)
    if stage == 0:
        if input == '0':
            stage = 1
            header()
        elif input == '1':
            printer.clear()
            printer.append(msg)
        elif input == '2':
            extract()
        elif input == '3':
            printer.clear()
            printer.append(html)
        elif input == '4':
            printer.clear()
            with open(f'E-mail.html', 'w+') as f:
                f.write(html)
        elif input == '5':
            printer.clear()
            checkIP()
        elif input == '000':
            https.terminate()
            sys.exit(0)
        else:
            printer.clear()
            print('\033c')
    elif stage == 1:
        if int(input) <= len(tags):
            hexec(int(input))

def banner():
    global counter
    if counter == 0:
        cprint(logo, style=colors())
        counter = 1
    else:
        cprint(logoy, style=colors())
        counter = 0
    cprint(resume, style=colors())
    banner = ''
    for option in context:
        banner += f'\n{context.index(option)}- {option}'
    print(banner)
    for i in printer:
        print('\n\n', i)

def parse(email, loop):
    global cc, rp, xtm, aut, spf, rspf, msg, mfrom, to, subject, date, headers, tags, html
    try:
        mail = parse_email(email)
    except ParseError as e:
        print('Falha ao carregar arquivo:', e)
        sys.exit(1)
    try:
        subject = mail.subject
    except:
        pass
    try:
        date = mail.date
    except:
        pass
    try:
        mfrom = cat(mail.headers['From'], 'email')
    except:
        pass
    try:
        to = cat(mail.headers['To'], 'email')
    except:
        pass
    try:
        xtm = mail.headers['X-TM-Authentication-Results']
    except:
        pass
    try:
        aut = mail.headers['Authentication-Results']
    except:
        pass
    try:
        spf = mail.headers['X-TM-Received-SPF']
    except:
        pass
    try:
        rspf = mail.headers['Received-SPF']
    except:
        pass
    try:
        cc = mail.headers['Cc']
    except:
        pass
    try:
        rp = mail.headers['Return-Path']
    except:
        pass
    try:
        html = mail.text_html[0]
    except:
        pass

    for msgs in mail.text_plain:
        msg = msg + msgs

    try:
        for tag in mail.headers:
            headers[tag] = mail.headers[tag]
            tags.append(tag)
    except:
        pass

    try:
        for att in mail.attachments:
            if len(att.filename.strip().replace(' ', '').replace('\n', '')) >= 1:
                attachments.append(att.filename)
            else:
                pass
    except:
        pass

parse(email, None)

if len(attachments) == 1:
   attachment = attachments[0]
else:
    attachment = ''
    for i in attachments:
        attachment += i


urlm = re.findall(regex, msg)
for url in urlm:
    if url in murl:
        pass
    else:
        murl.append(url)
urlh = re.findall(regex, html)
for url in urlh:
    if url in hurl:
        pass
    else:
        hurl.append(url)

while True:
    try:
        usedport.clear()
        usedport.append(port())
        https = Process(target=http, args=(usedport[0],))
        https.start()
        break
    except:
        pass

resume = f'''
[bold]Remetente:[/bold] {mfrom}
[bold]Destinatário:[/bold] {to}
[bold]Cc:[/bold] {cc}
[bold]Assunto:[/bold] {subject}
[bold]Data:[/bold] {date}
[bold]Anexos:[/bold] {attachment}
[bold]X-TM-Authentication-Results:[/bold] {xtm}
[bold]Authentication-Results:[/bold] {aut}
[bold]X-TM-Received-SPF:[/bold] {spf}
[bold]Received-SPF:[/bold] {rspf}
[bold]Return-Path:[/bold] {rp}
[bold]URLs no corpo do eml:[/bold] {murl}
[bold]URLs no HTML:[/bold] {hurl}
[bold]HTTP Server:[/bold] http://localhost:{usedport[0]}
'''

while True:
    context = stages[stage]
    print('\033c')
    banner()
    ask()
