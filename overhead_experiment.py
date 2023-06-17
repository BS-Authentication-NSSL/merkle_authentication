import base64
import datetime
import os
import sys
import time

#algorithms = ['rsa512', 'rsa1024', 'rsa2048', 'rsa4096', 'secp112r1', 'secp112r2', 'secp128r1', 'secp128r2', 'secp160k1', 'secp160r1', 'secp160r2', 'secp192k1', 'secp224k1', 'secp224r1', 'secp256r1', 'secp384r1', 'secp521r1', 'prime192v1', 'prime192v2', 'prime192v3', 'prime239v1', 'prime239v2', 'prime239v3', 'prime256v1', 'sect113r1', 'sect113r2', 'sect131r1', 'sect131r2', 'sect163k1', 'sect163r1', 'sect163r2', 'sect193r1', 'sect193r2', 'sect233k1', 'sect233r1', 'sect239k1', 'sect283k1', 'sect283r1', 'sect409k1', 'sect409r1', 'sect571k1', 'sect571r1']
algorithms = ['rsa512', 'rsa1024', 'secp384r1', 'prime256v1']

numSamples = 10000

def terminal(cmd):
	return os.popen(cmd).read()

# Return the number of seconds to compute the function
def timeCommand(cmd):
	t1 = time.perf_counter()
	response = os.popen(cmd).read()
	t2 = time.perf_counter()
	response = response.strip().replace('\n', ' ')
	if len(response) == 0: response = 'Blank'
	return (t2 - t1) * 1000, response

def header():
	line = 'Timestamp,'
	line += 'Timestamp (s),'
	line += 'Hash Algorithm,'
	line += 'Signature Algorithm,'
	line += 'Key Generation (ms),'
	line += 'Message Sign (ms),'
	line += 'Message Verify (ms),'
	line += 'Response to Key Generation,'
	line += 'Response to Message Sign,'
	line += 'Response to Message Verify,'
	line += 'Public Size (B),'
	line += 'Private Size (B),'
	line += 'Signature Size (B),'
	line += 'Message Size (B),'
	# line += 'SIB 1 Generation Time (ms),'
	# line += 'SIBs Generation Time (ms),'
	# line += 'SIB Packing Time,'
	# line += 'Overall Handshake Time (ms),'
	# line += 'Overall Handshake Size (B),'
	return line

def log(algorithm, j):
	now = datetime.datetime.now()
	seconds = (now - datetime.datetime(1970, 1, 1)).total_seconds()
	hash_algorithm = 'SHA-256'
	# algorithm = terminal('head -n 1 configs/signature_algorithm_to_use.txt').strip()
	# if algorithm == 'RSA':
	# 	algorithm = 'rsa2048'
	# elif algorithm == 'ECDSA':
	# 	algorithm = 'secp384r1'
	line = str(now) + ','
	line += str(seconds) + ','
	line += hash_algorithm + ','
	line += algorithm + ','
	durationKeygen, messageKeygen = timeCommand('cd certificates_base_station; ./make_keys.sh ' + algorithm)
	durationSign, messageSign = timeCommand('cd certificates_base_station; ./sign_file.sh message_to_sign.json')
	durationVerify, messageVerify = timeCommand('cd certificates_base_station; ./verify_file.sh message_to_sign.json')
	line += str(durationKeygen) + ','
	line += str(durationSign) + ','
	line += str(durationVerify) + ','
	line += '"' + messageKeygen + '",'
	line += '"' + messageSign + '",'
	line += '"' + messageVerify + '",'
	line += str(os.path.getsize('certificates_base_station/base_station_public.key')) + ','
	line += str(os.path.getsize('certificates_base_station/base_station_private.key')) + ','
	line += str(os.path.getsize('certificates_base_station/base_station_signature.sig')) + ','
	line += str(os.path.getsize('certificates_base_station/message_to_sign.json')) + ','

	durationDeploy = 'N/A'
	messageDeploy = 'N/A'

	pubKeyFile = open('certificates_base_station/base_station_public.key', 'r')
	publicKey = base64.b64encode(pubKeyFile.read().encode('ascii'))
	pubKeyFile.close()

	cellID = str(105217 + j)

	# line += 'SIB 1 Generation Time (ms),'
	# line += 'SIBs Generation Time (ms),'
	# line += 'SIB Packing Time,'
	# line += 'Overall Handshake Time (ms),'
	# line += 'Overall Handshake Size (B),'
	return line


outputFile = open('overhead_experiment.csv', 'w')
outputFile.write(header() + '\n')

for i in range(numSamples):
	for j in range(len(algorithms)):
		algorithm = algorithms[j]
		print(f'Sample {i + 1} of {numSamples}, Algorithm {j + 1} of {len(algorithms)}')
		outputFile.write(log(algorithm, j) + '\n')

outputFile.close()
