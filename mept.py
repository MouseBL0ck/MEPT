#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import sys, os
import getpass
import smtplib
import email.message

import thread

def banner():

    print """
            _.-^^---....,,--       
         _--                  --_  
        <                        >)
        |                         | 
        \._                   _./  
            ```--. . , ; .--'''       
                  | |   |             
               .-=||  | |=-.   
               `-=#$%&%$#=-'   
                  | ;  :|     
         _____.,-#%&$@%#&#~,._____
    *============================================*
    *         MEPT Email Phishing                *
    *                                            *
    *  By: Mouse_BL0ck                           *
    *                                            *
    *  I have no responsibility for              *
    *  using the script.                         *
    *============================================*
"""


def getTemplate(social_template, var_name, var_link):

    raw_template = open('Templates/%s' %(social_template), 'r').read()
    
    template = raw_template.replace(r'{var_name}', var_name).replace(r'{var_link}', var_link)

    return template


def messageMaker(smtp_user,  target_email, template):

    base_message = email.message.Message()
    base_message['Subject'] = 'Seguraca da conta'
    base_message['From'] = smtp_user
    base_message['To'] =  target_email
    base_message.add_header('Content-Type','text/html')
    base_message.set_payload(template)

    return base_message.as_string()


def smtpConnection(smtp_addr, smtp_user, smtp_pass):

    try:
        smtp_connection = smtplib.SMTP(smtp_addr)
        smtp_connection.ehlo()
        smtp_connection.starttls()
    
    except Exception as smtp_server_error:
        print smtp_server_error, '\n    [!] Server error.'
    
    try:
        smtp_connection.login(smtp_user, smtp_pass)
        return smtp_connection
    
    except Exception as smtp_login_error:
        print smtp_login_error, '\n    [!] Login error, try again.'
        sys.exit(1)


def threadStart(smtp_addr, smtp_user, smtp_pass, template, phishing_link, wordlist_file, n_threads):

    target_list = []
    wordlist_lines = 0

    for i in wordlist_file:
        wordlist_lines += 1
        target_list.append(i)

    email_packages = int(wordlist_lines / n_threads)

    if ((wordlist_lines % n_threads) == 0):
        email_packages_range = 0
        
        for z in range(0, n_threads, 1):

            send_packages = int((z+1) * email_packages)
            print '\n    [%s] Thread [%i] packages' %(z, send_packages)            
            
            thread.start_new_thread(sendWithThread, (smtp_addr, smtp_user, smtp_pass, template, phishing_link, send_packages, email_packages_range, target_list))
            email_packages_range = send_packages
        
        print '\n    [+] Finishing... To exit CTRL+C.\n\n'  
        return True
            
    else:
        email_packages_range = 0

        for z in range(0, n_threads, 1): 
            
            send_packages = int((z+1) * email_packages)
            print '\n    [%s] Thread [%i] packages' %(z, send_packages)

            if (z == n_threads -1):
                thread.start_new_thread(sendWithThread, (smtp_addr, smtp_user, smtp_pass, template, phishing_link, (send_packages+1), email_packages_range, target_list))

            else:
                thread.start_new_thread(sendWithThread, (smtp_addr, smtp_user, smtp_pass, template, phishing_link, send_packages, email_packages_range, target_list))
                email_packages_range = send_packages

        print '\n    [+] Finishing... To exit CTRL+C.\n\n'
        return True


def sendWithThread(smtp_addr, smtp_user, smtp_pass, template, phishing_link, email_packages, email_packages_range, target_list):
    
    for i in range(email_packages_range, email_packages, 1):

        try:
            smtp_object = smtpConnection(smtp_addr, smtp_user, smtp_pass)

            target_name = target_list[i].split('@')[0]
            email_body = messageMaker(smtp_user, target_list[i], getTemplate(template, target_name, phishing_link))

            smtp_object.sendmail(smtp_user, target_list[i], email_body)

            print '\n    [+] %s Sent.' %(target_list[i])
                    
        except Exception as sendwiththread_error:
            print sendwiththread_error
    
    return True


def main():
    
    banner()
    
    try:
        attack_type = int(raw_input('    Attacks\n\n    [1]Single Target\n    [2]Wordlist :'))
    
    except:
        print '\n    Invalid input.'
        sys.exit(1)

    smtp_addr = str(raw_input('\n    SMTP Server (smtp.gmail.com:587) :'))
    smtp_user = str(raw_input('\n    SMTP Email :'))
    smtp_pass = str(getpass.getpass('\n    SMTP Password :'))
    phishing_link = str(raw_input('\n    Phishing Link :'))
    template = str(raw_input('\n    Template (Tfacebook.html, Tgmail.html, Thotmail.html) :'))

    if (attack_type == 1):

        target_email = str(raw_input('\n    Target Email :'))

        target_name = target_email.split('@')[0]

        smtp_object = smtpConnection(smtp_addr, smtp_user, smtp_pass)
        email_body = messageMaker(smtp_user, target_email, getTemplate(template, target_name, phishing_link))

        try:
            smtp_object.sendmail(smtp_user, target_email, email_body)
            print '\n    [+] %s Sent.' %(target_email)
            print '\n    [+] Complete.'
            smtp_object.quit()
            sys.exit(0)

        except Exception as smtp_send_error:
            print smtp_send_error, '\n    [!] Error in email send.'
            smtp_object.quit()
            sys.exit(1)
        

    elif (attack_type == 2):

        targets_email_file_location = str(raw_input('\n    Target Wordlist (/home/user/wordlist.txt) :'))
        threads = int(raw_input('\n    Threads : '))

        wordlist_file = open(targets_email_file_location, 'r')

        if (threads == 1):
            for target in wordlist_file:
                
                target_name = target.split('@')[0]
                email_body = messageMaker(smtp_user, target, getTemplate(template, target_name, phishing_link))

                try:
                    smtp_object.sendmail(smtp_user, target, email_body)
                    print '\n    [+] %s Sent.' %(target)

                except Exception as smtp_send_error:
                    print smtp_send_error, '\n    [!] Error in email send.'
                
        elif (threads > 1):
            threadStart(smtp_addr, smtp_user, smtp_pass, template, phishing_link, wordlist_file, threads)
           
            try:
                while (True):
                    pass
                    
            except KeyboardInterrupt:
                os.system('clear')
                banner()
                print '\n    Bie...'
                sys.exit(2)
        
        else:
            print '\n    Invalid input.'
            sys.exit(1)

    else:
        print '\n    Invalid input.'
        sys.exit(1)

if __name__ == '__main__':
    main()