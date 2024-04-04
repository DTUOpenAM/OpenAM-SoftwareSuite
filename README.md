Installation
==================================

.. _Git: https://git-scm.com/downloads

OpenAM software for 3D printing

Software requirements:
	* In order to run some of the external libraries, you may need to install a c++ compiler. The c++ libraries were compiled and tested with MSVC. You can find it here: https://visualstudio.microsoft.com/visual-cpp-build-tools/ . When installing, select the *desktop development with C++* option.

To get the software:
	* Install `Git`_ .
	* open "Git Bash".
	* move to the installation directory (e.g. ``cd Documents``)
	* run::
	
		git clone https://github.com/andrea-luongo/3DOpenSource_development.git   # temporary private
		
	
	* The BVH/ray intersection C++ source code can be found here: https://github.com/andrea-luongo/ray_tracer_pywrapper. (Public repo)
	* The PyWrapper for the clearpathSCSK and VisitechLRS4KA can be found here: https://github.com/andrea-luongo/dlp_pywrappers/tree/master/kpdlpPyWrapper (Private repo)
	  (if you don't have access to the repo, provide your github username to seaa@mek.dtu.dk).

To update the software:
	- open "Git Bash"
	- move to the installation directory (e.g. ``cd Documents/3DOpenSource``)
	- run::
	
		git pull 
		

To Install on win-64:
	- install Anaconda 64 bits
	- open "3DOpenSource/resources"
	- open "Anaconda Prompt" in the location of the software installation
	- run::
		
		conda env create -f environment.yaml
		
	- if you want to use the VisitechLRSWQ projector you also need to install "dln.3.0.2.exe", and place the i2c_cmd.exe under ./resources
		

To Update Anaconda environment:
	- open "Anaconda Prompt" in the location of the software installation
	- run::

		conda activate 3DOpenSource
		conda env update --file environment.yaml --prune
		

To Run on win-64:
	- open "Anaconda Prompt" in the location of the software installation
	- run::

		conda activate 3DOpenSource
		python __main__.py
		



