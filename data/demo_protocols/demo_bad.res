#This is a comment! 
#Should pass
da228358c6a3af6c82db6133337b79af067cbe5d8814bc5212446b2b4b59e0e3|0|[('  key_deducible (exists-trace)', 'TRUE', '5')]|0.32868170738220215|
#Should exhibit FAIl, INC, DEC
34a8232603cc1b7358fc2d267ff35824910a0e7d859c20077bdc61c3279357fe|0|[('  types (all-traces)', 'FALSE', '33'), ('  nonce_secrecy (all-traces)', 'TRUE', '100'), ('  injective_agree (all-traces)', 'TRUE', '1'), ('  session_key_setup_possible (exists-trace)', 'TRUE', '5')]|1.448804537455241|
#Should timeout
ba94ba9d7c8f971d014ba8d15195e5bfa8a08a6f65cba316b625fe626d0ec1bb|0|[('  types (all-traces)', 'TRUE', '37'), ('  nonce_secrecy (all-traces)', 'TRUE', '133'), ('  session_key_setup_possible (exists-trace)', 'TRUE', '9')]|0.2000|
#Should INC 
82857fb41dcaf981ffe47a0467a280576df08e5721c08f07c9c5e048ca47518a|0|[('  types (all-traces)', 'TRUE', '33'), ('  nonce_secrecy (all-traces)', 'FALSE', '10'), ('  injective_agree (all-traces)', 'FALSE', '14'), ('  session_key_setup_possible (exists-trace)', 'TRUE', '5')]|1.898511012395223|
#Should DEC
77b85dcee6aacfd437d6fa1040757356061378ba43ce76c029a40a466ff5e1ae|0|[('  session_key_secrecy (all-traces)', 'TRUE', '38'), ('  injective_agree (all-traces)', 'TRUE', '369'), ('  session_key_setup_possible (exists-trace)', 'TRUE', '11')]|1.507434368133545|
#Should OVERTIME but pass with correct command line arguments
f3a69fea3c77e0a021da6cf7e70a2fbf1341cf918684510d0c07f4a75cf5cb3c|0|[('  Client_session_key_secrecy (all-traces)', 'TRUE', '5'), ('  Client_auth (all-traces)', 'TRUE', '11'), ('  Client_auth_injective (all-traces)', 'TRUE', '15'), ('  Client_session_key_honest_setup (exists-trace)', 'TRUE', '5')]|17.00|
#Should be missing - hash edited
8b8f75ddbfffdcf43d1a34db99d3de323777e47ac6c0d0a35067264aaaaaaaaa|0|[('  UM_secure_responder (all-traces)', 'TRUE', '33')]|0.5484058856964111|
#Should FAIL
0c0e03183d8a0e2053d74bb2773e84427a3d6d0cd12ee6e6b9693502c293432d|0|[('  UM_executable (exists-trace)', 'FALSE', '9')]|0.36014850934346515|
