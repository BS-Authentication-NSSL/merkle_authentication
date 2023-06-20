#ifndef SRSRAN_HANDSHAKE_PROOF_CPP
#define SRSRAN_HANDSHAKE_PROOF_CPP

// This code is created by the Cybersecurity Lab, University of Colorado, Colorado Springs, 2022

#include <iostream>
#include <filesystem>
#include <fstream>
#include <vector>
#include <string>
#include <regex>
#include "handshake_proof_merkle.cc"
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wsubobject-linkage"

// Cybersecurity Lab: Hashing support
#include <openssl/sha.h> // SHA-256
# ifdef OPENSSL_NO_SHA256
  #include <openssl/evp.h> // EVP SHA-256
# endif

// Cybersecurity Lab:Random string
#include <random>
#include <string>
#include <sstream>
#include <iomanip>



class HandshakeProof {
    private:
        bool initialized = false;
        HandshakeProofTreeT<32, sha256_compress> merkleTree;
        std::string merkleHash = "";

        // The function used to sort the vector of file names
        static bool pathCompareFunction (std::string a, std::string b) {
            return a < b;
        }

        // Recursively list the files in a directory
        std::vector<std::string> getFiles(std::string directory, std::string regexToIncludeStr, std::string regexToIgnoreStr) {
            std::vector<std::string> files;
            for(std::filesystem::recursive_directory_iterator i(directory), end; i != end; ++i) {
                if(!is_directory(i->path())) {
                    std::string str = i->path();
                    if(std::regex_match(str, std::regex(regexToIncludeStr)) && !std::regex_match(str, std::regex(regexToIgnoreStr))) {
                        files.push_back(str);
                    }
                }
            }
            std::sort(files.begin(),files.end(), pathCompareFunction);
            return files;
        }

        // Given a number (e.g. 10) compute the next power of two (e.g. 16)
        int nextPowerOfTwo(int num) {
            double n = log2(num);
            return (int)pow(2, ceil(n));
        }

    public:

        std::string generateProof(std::string ID) {
            if(!initialized) initialize();
            // Update the ID
            if(ID == "::") {
                ID = generateRandomBytes(4);
                std::cout << "\nChanged ID from \"::\" to \"" << ID << "\"" << std::endl;
            }
            std::cout << "\nGenerating handshake proof for \"" << ID << "\"" << std::endl;
            updateHashAtIndex(merkleTree, 0, sha256(ID));
            return ID + "@" + merkleTree.root().to_string();
        }

        bool verifyProof(std::string combined) {
            std::string ID, hash;
            std::regex rgx("([^@]+)@(.+)");
            std::smatch matches;
            if(std::regex_search(combined, matches, rgx)) {
                ID = matches[1].str();
                hash = matches[2].str();
            } else {
                // Invalid format, verification failed
                std::cout << "\nHandshake proof \"" << combined << "\" was in the wrong format" << std::endl;
                return false;
            }
            std::cout << "\nVerifying handshake proof for \"" << ID << "\"" << std::endl;

            updateHashAtIndex(merkleTree, 0, sha256(ID));
            std::string proof = merkleTree.root().to_string();
            std::cout << "\n\"" << proof << "\" == \"" << hash << "\"" << std::endl;
            return proof == hash;
        }

        // Update the hash at an index within the merkleTree
        void updateHashAtIndex(HandshakeProofTree &merkleTree, int index, std::string hashString) {
            HandshakeProofTreeT<32, sha256_compress>::HandshakeProofNode* ID = merkleTree.walk_to(index, true, [](HandshakeProofTreeT<32, sha256_compress>::HandshakeProofNode* n, bool go_right) {
                n->dirty = true;
                return true;
            });
            HandshakeProofTree::Hash newHash(hashString);
            ID->hash = newHash;
            merkleTree.compute_root();
        }

        std::string getHash() {
            return merkleHash;
        }

        void initialize() {
            if(initialized) return;
            std::cout << "\nHandshake prover is being initialized..." << std::endl;
            std::string currentPath(std::filesystem::current_path());
            std::cout << "\nCurrent path = " << currentPath << std::endl;

            // Get the list of code file names
            std::string directory = ".";
            std::string regexToIncludeStr = ".*(\\.cpp|\\.c|\\.h|\\.cc|\\.py|\\.sh)";
            std::string regexToIgnoreStr = ".*(/MerkleTree/).*";
            // Get the list of code file names
            std::vector<std::string> files = getFiles(directory, regexToIncludeStr, regexToIgnoreStr);
            std::vector<std::string> hashes ((int)files.size());
            // Compute the hash of the files
            for(int i = 0; i < (int)files.size(); i++) {
                //std::cout << "!!! " << files[i] << std::endl;
                hashes.at(i) = sha256(getContents(files[i]));
            }
            // Set the initial ID
            hashes.insert(hashes.begin(), "0000000000000000000000000000000000000000000000000000000000000000");
            // Adjust the size to make it a full binary merkleTree
            int targetSize = nextPowerOfTwo((int)hashes.size()), i = 0;
            while((int)hashes.size() < targetSize) {
                hashes.push_back(hashes.at(i));
                i++;
            }

            // Cybersecurity Lab: Testing a mini merkleTree
            // std::vector<std::string> hashes (16);
            // for(int i = 0; i < 16; i++) {
            //  hashes.at(i) = sha256(to_string(i + 1));
            // }

            // Convert the hashes to Merkle node objects
            std::vector<HandshakeProofTree::Hash> leaves ((int)hashes.size());
            for(int i = 0; i < (int)hashes.size(); i++) {
                HandshakeProofTree::Hash hash(hashes.at(i));
                leaves.at(i) = hash;
            }

            // Create the merkleTree
            HandshakeProofTreeT<32, sha256_compress> newMerkleTree;
            merkleTree = newMerkleTree;
            merkleTree.insert(leaves);

            // Update the ID
            updateHashAtIndex(merkleTree, 0, "0000000000000000000000000000000000000000000000000000000000000000");

            merkleHash = merkleTree.root().to_string();
            initialized = true;
        }

        // Read the contents of a file at a given file path
        static std::string getContents(std::string filePath) {
            std::string contents = "";
            std::ifstream f(filePath);
            while(f) {
                std::string line;
                getline(f, line);
                contents += line + '\n';
            }
            return contents;
        }

        // Write some contents to src/temporary_file.sh, to update the merkle hash and make it invalid, returns 0 if successful, and 0 if unsuccessful
        bool writeTempFileContentsAndRegenerateTree(std::string contents) {
            std::ofstream out("./src/temporary_file.sh");
            out << contents;
            out.close();
            initialized = false;
            initialize();
            return 1;
        }

        // Read the contents of src/temporary_file.sh
        static std::string readTempFileContents() {
            return getContents("./src/temporary_file.sh");
        }

        // Generate N random bytes in hex format
        static std::string generateRandomBytes(std::size_t N) {
            std::random_device rd;
            std::default_random_engine generator(rd());
            std::uniform_int_distribution<int> distribution(0, 255);

            std::ostringstream oss;
            for (std::size_t i = 0; i < N; ++i) {
                int random_byte = distribution(generator);
                oss << std::hex << std::setw(2) << std::setfill('0') << random_byte;
            }

            return oss.str();
        }

        // Computes the SHA-256 hash of a string
        # ifdef OPENSSL_NO_SHA256 // Determine whether or not to use EVP
            static bool computeHash(const std::string& unhashed, std::string& hashed) {
            bool success = false;
            EVP_MD_CTX* context = EVP_MD_CTX_new();
            if(context != NULL) {
                if(EVP_DigestInit_ex(context, EVP_sha256(), NULL)) {
                    if(EVP_DigestUpdate(context, unhashed.c_str(), unhashed.length())) {
                        unsigned char hash[EVP_MAX_MD_SIZE];
                        unsigned int lengthOfHash = 0;
                        if(EVP_DigestFinal_ex(context, hash, &lengthOfHash)) {
                            std::stringstream ss;
                            for(unsigned int i = 0; i < lengthOfHash; ++i) {
                                ss << std::hex << std::setw(2) << std::setfill('0') << (int)hash[i];
                            }
                            hashed = ss.str();
                            success = true;
                        }
                    }
                }
                EVP_MD_CTX_free(context);
            }
            return success;
            }

            static std::string sha256(std::string message) {
                std::string hash;
                computeHash(message, hash);
                return hash;
            }
        # else
            static std::string sha256(std::string message) {
                unsigned char hash[SHA256_DIGEST_LENGTH];
                SHA256_CTX sha256;
                SHA256_Init (&sha256);
                SHA256_Update (&sha256, message.c_str(), message.size());
                SHA256_Final (hash, &sha256);
                std::stringstream ss;
                for(int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
                    ss << std::hex << std::setw(2) << std::setfill('0') << (int)hash[i];
                }
                return ss.str();
            }
        # endif
};

#pragma GCC diagnostic pop
#endif // SRSRAN_HANDSHAKE_PROOF_CPP