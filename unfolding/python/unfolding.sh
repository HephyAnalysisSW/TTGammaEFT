#!/bin/sh
python unfolding.py --extended --settings observed_ptG_RunII
python unfolding.py --extended --settings observed_absEta_RunII
python unfolding.py --extended --settings observed_dRlg_RunII

python unfolding.py --extended --settings observed_ptG_2016
python unfolding.py --extended --settings observed_absEta_2016
python unfolding.py --extended --settings observed_dRlg_2016

python unfolding.py --extended --settings observed_ptG_2017
python unfolding.py --extended --settings observed_absEta_2017
python unfolding.py --extended --settings observed_dRlg_2017

python unfolding.py --extended --settings observed_ptG_2018
python unfolding.py --extended --settings observed_absEta_2018
python unfolding.py --extended --settings observed_dRlg_2018

#python unfolding.py --extended --settings expected_ptG_RunII
#python unfolding.py --extended --settings expected_absEta_RunII
#python unfolding.py --extended --settings expected_dRlg_RunII
