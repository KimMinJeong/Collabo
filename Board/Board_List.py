# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, g, session, flash, \
     redirect, url_for, abort
from flask_openid import OpenID
from openid.extensions import pape
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from os.path import dirname, join


