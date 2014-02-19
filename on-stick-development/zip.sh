#!/bin/bash

read -p "enter project folder > " folder

cd $folder
mkdir user
cp *.py user/

zip -r ../robot.zip user/

rm -rf user/
