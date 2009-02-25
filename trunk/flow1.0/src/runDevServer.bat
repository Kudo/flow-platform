set PYTHONPATH=%PYTHONPATH%;%CD%\flow-site;%PYTHONPATH%;%CD%\flow-site\lib
python "%ProgramFiles%\Google\google_appengine\dev_appserver.py" flow-site %1 %2 %3 %4 