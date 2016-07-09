rm data/demo_protocols/demo.res
asciinema -y -c  "./dist/tamarin-tester /home/dennis/.local/bin/tamarin-prover -p data/demo_protocols/ --input data/demo_protocols/demo_good.res"
asciinema -y -c  "./dist/tamarin-tester /home/dennis/.local/bin/tamarin-prover -p data/demo_protocols/ --input data/demo_protocols/demo_bad.res -mp 2 --overtime"
asciinema -y -c  "./dist/tamarin-tester /home/dennis/.local/bin/tamarin-prover -p data/demo_protocols/ --benchmark -mp 15 -mc 10 --output data/demo_protocols/demo.res"
rm data/demo_protocols/demo.res