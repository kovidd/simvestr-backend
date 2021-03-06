# Simvestr

Back end of the investment simulator project for COMP9900

## Getting Started
[comment]: <> (TODO)
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites
[comment]: <> (TODO: expand on this as we go)
All pre-requisites are listed in [requirements.txt](requirements.txt). They have also been packaged in the distribution, which is the preferred method for installing the application.


### Development Setup
[comment]: <> (TODO: check that this procedure works on CSE/team pcs)
First, setup your virtual environment. You can use the venv package.

```
path_to_app $ python3.7 -m venv .simvestr
```

##### Activating venv

OSX or Linux:

```
path_to_app $ source .simvestr/bin/activate
(.simvestr) path_to_app $ 
```

Windows:

```
path_to_app>.\simvestr\Scripts\activate
(.simvestr) path_to_app>
```

##### Dependencies

Now  ```pip```  install the the application from the distribution, it contains all the dependencies needed:

```
(.simvestr) ($ or >) pip install dist/simvestr-1.0.0.tar.gz
```


The source code can then be seen in the ```~/your_virtual_environment/lib/site-packages/simvestr``` folder.

## Running the app

The production server has been setup to run in a Unix environment. We have built a helper script for Windows, but note this will only launch the Flask debug server and is not suitable for production use.

OSX or Linux:

If the virtual environment created in the Getting Started section is not active, please activate it or re-visit the section to ensure a virtual environment is made.

If you're running the app for the first time and the database needs to be setup, run the following command within the virtual environment with the ```run_setup``` flag equal to ```True```.  This will start the server and intialise the database.

```
(.your_env) path_to_app $ gunicorn "simvestr:create_app(run_setup=False)" --bind <host>:<port>
```

If the database has already been setup by running the above command, toggle the ```run_setup``` flag to ```false```. 

Common ```host```'s and ```port```'s are ```0.0.0.0``` and ```5000``` respectively for running in a local environment. To work with the Front-end application however, please use ```host=127.0.0.1``` and ```port=5000``` .


Windows:

To run from windows, the source code is required. Assuming that the tarball has been installed (and as such, the dependencies), the ```run.py``` script (whcih is stored at the root of the source code) can be used to run the application. 

```
(.your_env) path_to_source_code > python3 run.py
```

## Running the tests
[comment]: <> (TODO)
To run the tests, the source code is required.

Navigate to the root directory of the source code and simply run:
```
(.your_env) path_to_app $ pytest
```

## Authors
[comment]: <> (TODO)
|Name | zID | Email|
| --- | --- | ---- |
| Jihad Meraachli | z5156156 | j.meraachli@student.unsw.edu.au | 
| Khan Schroder-Turner | z5020362 | k.schroder-turner@student.unsw.edu.au | 
| Kovid Sharma | z5240067 | k.sharma.1@student.unsw.edu.au | 
| Simon Garrod | z3264122 | s.garrod@student.unsw.edu.au | 
| Timothy Brunette | z5233368 | t.brunette@student.unsw.edu.au | /project/contributors) who participated in this project.

## License
[comment]: <> (TODO)
This project is licensed under the GNU AFFERO GENERAL PUBLIC LICENSE v3 - see the [LICENSE.md](LICENSE.md) file for details