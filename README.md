# tRecs2 Requirements and set up

1. Download python3 and install

2. Download tRecs from git

4. Navigate to the tRecs directory in terminal or command prompt

5. If you want to use a virtual environtment create a virtual environment:

	5a. open a terminal or console window
	
	5b. type: python3 -m venv venv
	
	5c. select virtual envrionment:
	
		windows type: venv\Scripts\activate.bat
		
		mac type: source venv/bin/activate
		
6. install requirements:

	type: pip install -r requirements.txt


============================================================================
# tRecs usage

Track reconstruction tool for Imairs. Because cells divide...

The experiment path should contain all output data from imaris for a given experiment as .csv files.

Cells should be tracked from division to division. Daughter cell tracks should start in the next frame.

tRecs will then join the mothers to daughters. It will also give 


usage: tRecs2.py [-h] [--time TIME] experiment_path

positional arguments:
  experiment_path       The location of the folder which contains all of the
                        output csv files from Imaris

optional arguments:
  -h, --help            show this help message and exit
  --time TIME, -t TIME  the time interval in mins for the imaging, the default
                        value is 10 minutes



==================================================================================

# makeGPOSC

This will convert the output full tracks to a GPOSC compatible format. 

makeGPOSC.py takes the outputs from tRECs and makes GPosc compatable output files from full tracks

usage: makeGPOSC.py [-h] [-c C] [-v V] tRecs_file

positional arguments:
  tRecs_file

optional arguments:
  -h, --help         show this help message and exit
  -c C, -channel C   The channel as a integer number. Default == 2
  -v V, -variable V  The variable you wish to plot e.g "Intensity Mean".
                     Default == "Intensity Mean"

