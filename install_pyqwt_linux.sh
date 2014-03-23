mkvirtualenv env_qwt
mkdir tmp
cd tmp/
pip install numpy
wget http://www.riverbankcomputing.com/static/Downloads/sip4/sip-4.15.6-snapshot-0c1b13e45887.tar.gz
tar zxf sip-4.15.6-snapshot-0c1b13e45887.tar.gz 
cd sip-4.15.6-snapshot-0c1b13e45887/
python configure.py --incdir=$HOME/.virtualenvs/env_qwt/include
make
make install
cd ..
wget http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.10.4/PyQt-x11-gpl-4.10.4.tar.gz
tar zxf PyQt-x11-gpl-4.10.4.tar.gz 
cd PyQt-x11-gpl-4.10.4/
ls
python configure.py 
htop
make -j9
make install
wget "http://downloads.sourceforge.net/project/pyqwt/pyqwt5/PyQwt-5.2.0/PyQwt-5.2.0.tar.gz?r=http%3A%2F%2Fsourceforge.net%2Fprojects%2Fpyqwt%2F%3Fsource%3Ddlp&ts=1371067906&use_mirror=iweb"
mv "PyQwt-5.2.0.tar.gz?r=http:%2F%2Fsourceforge.net%2Fprojects%2Fpyqwt%2F?source=dlp&ts=1371067906&use_mirror=iweb" PyQwt-5.2.0.tar.gz
tar xvzf PyQwt-5.2.0.tar.gz
cd PyQwt-5.2.0/configure
python configure.py -Q ../qwt-5.2
make -j9
make install
cd ../..

python -c 'from PyQt4 import Qwt5'
