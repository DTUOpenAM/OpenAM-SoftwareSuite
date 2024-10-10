# 3DOpenSource Machine Control Software

## Overview

This project is an integrated solution for controlling LPBF (Laser Powder Bed Fusion) machines, offering a combination of slicing capabilities and serial communication with machines. Although active development has been discontinued, it remains a valuable resource for those seeking inspiration for developing their own machine control systems.

The software has been designed to handle the core functionalities needed for LPBF operations, including generating toolpaths, configuring process parameters, and establishing reliable communication between the software and the machine via a serial connection.

While there are limitations and the system is no longer updated, it can still be used with specific custom solutions. For developers and researchers, it provides a functional base from which to explore new ideas in the LPBF field.

## Core Functionalities

- **Slicing for LPBF Systems**: 
  The integrated slicer converts 3D models into layered toolpaths that are optimized for LPBF processes. It supports a variety of object types (e.g., contours, supports, hatches) and includes adjustable process parameters to suit different materials and printing strategies.

- **Serial Communication**:
  This software enables real-time communication with LPBF machines using a serial connection. It supports the execution of machine commands and the transmission of process data, ensuring smooth operation during the build process.

- **Parameter Customization**:
  Users can fine-tune laser power, scanning speed, and other critical parameters to optimize their build jobs. The software provides a flexible UI that allows for these adjustments on a per-layer or per-object basis.

- **Extensibility**:
  The project is built with modularity in mind. Although development has halted, the code is structured in a way that encourages further modification and experimentation. Its open nature provides a starting point for developers looking to extend its capabilities or repurpose its components.

## Status: Discontinued

While this project is no longer actively maintained, it remains a source of inspiration for anyone exploring LPBF machine control software development. Contributions are welcome if you'd like to continue evolving it, but please note that the original development team will not be providing further updates or support.

## Getting Started

To explore the project, simply clone the repository and set up the environment according to the provided dependencies. Although no new features are being added, the code remains a useful reference for those interested in LPBF systems and machine control software.





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
		



