@echo off

:: Create and activate virtual environment
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate

:: Install required packages
pip install -r requirements.txt

:: Ensure log directory exists
if not exist log (
    mkdir log
)

:: Clear any previous logs
del log\*.log

:: Run configScript.py separately to handle user input
echo Running configScript.py...
python configScript.py > log/configscript.log 2>&1
if %errorlevel% neq 0 (
    echo Error running configScript.py
    exit /b %errorlevel%
)
echo Finished running configScript.py

:: Run faker.py
echo Running faker.py...
python faker.py > log/faker.log 2>&1
if %errorlevel% neq 0 (
    echo Error running faker.py
    exit /b %errorlevel%
)
echo Finished running faker.py

:: Run consumer.py in a new terminal and capture its output
echo Running consumer.py...
start cmd /c "python consumer.py > log/consumer.log 2>&1"
echo Started consumer.py, waiting for it to initialize...

:: Wait for consumer.py to initialize (increase timeout if necessary)
timeout /t 15

:: Run emitter.py in a new terminal and capture its output
echo Running emitter.py...
start cmd /c "python emitter.py > log/emitter.log 2>&1"
echo Started emitter.py

:: Wait for 30 seconds to let the consumer run
timeout /t 30

:: Ask user to press any key to stop the consumer
echo The consumer is running. Please press any key to stop the consumer.
pause

:: Combine the log files into one log file in the desired order
echo Combining logs into combined_log.txt...
(
    type log\configscript.log
    type log\faker.log
    type log\emitter.log
    type log\consumer.log
) > out.txt
if %errorlevel% neq 0 (
    echo Error combining log files
    exit /b %errorlevel%
)
echo Logs have been combined into out.txt.

:: Display out.txt content:
echo Displaying out.txt content:
type out.txt

pause
