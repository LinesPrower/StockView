rd /S /Q dist
%python_dir%python setup.py py2exe
xcopy help dist\help /i /e /y