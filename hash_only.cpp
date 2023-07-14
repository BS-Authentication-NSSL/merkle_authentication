#include "handshake_proof_merklecpp.h"
#include "openssl/sha.h"
#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <regex>
#include <string>
#include <vector>


std::string sha256(const std::string str)
{
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256_CTX sha256;
    SHA256_Init(&sha256);
    SHA256_Update(&sha256, str.c_str(), str.size());
    SHA256_Final(hash, &sha256);
    std::stringstream ss;
    for(int i = 0; i < SHA256_DIGEST_LENGTH; i++)
    {
        ss << std::hex << std::setw(2) << std::setfill('0') << (int)hash[i];
    }
    return ss.str();
}




int main() {
	int numSamples = 5000;

	std::string fileName = "Algorithm_benchmark_Hash_Only" + std::to_string(numSamples) + ".csv";

	std::ofstream outputFile;
	outputFile.open(fileName);

	std::string header = "";
	header += "Total Time (us),";
    header += "Single Time (us),";
	outputFile << header << std::endl;
    
    std::string hash_string = "I want to generate hash of this string. This is a dummy string. Although it should be the contents of the file but I think this is Okay!";

    std::clock_t t1_readHashContents = std::clock();
    for(int i = 0; i < numSamples; i++) {
		std::string hash = sha256(hash_string);

				//std::cout << "File \"" << files.at(i) << "\" has has \"" << hashes.at(i) << "\"" << std::endl;
		}
	std::clock_t t2_readHashContents = std::clock();

    double usTotaltime = (t2_readHashContents - t1_readHashContents) / (double)(CLOCKS_PER_SEC);
    double usSingletime = usTotaltime / numSamples;


    std::string row = "";

	row += std::to_string(usTotaltime) + ",";
	row += std::to_string(usSingletime) + ",";


	outputFile << row << std::endl;


	return 0;
}