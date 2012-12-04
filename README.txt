README

To run NimGame, include all files in the same directory. To run the server, go to the directory where the files are stored and run:

	python server.py

It will bind to the machine where it is located, on port 7777.

To connect to the server, go to the directory where the client file is located, and run:

	python client.py hostname 7777

where hostname is the address of the machine which the server is running on. The client will then accept the commands:

	help, login, remove, who, games, play, bye

explained in the larger documentation
