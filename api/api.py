import requests
import json
from flask import request
from flask import Response
from flask import json
from api import bp
import psycopg2
from psycopg2 import *
import math
from dotenv import load_dotenv
from os import environ 

load_dotenv('.env')
BASE_URL=environ.get('BASE_URL')
DB_CONFIG=environ.get('DB_CONFIG')

@bp.route('/search_movies', methods=['GET'])
def search_movies():
    try:
        connection = psycopg2.connect(DB_CONFIG)
        cursor = connection.cursor()
        query = request.args['title']
        page = request.args['page']
        response = requests.request("GET", BASE_URL + '&s=' + query + '&page=' + page)
        json_response = response.json()
        no_of_pages = math.ceil(float(json_response['totalResults'])/10)
        insert_query = "INSERT INTO movies (ID, TITLE, YEAR, POSTER, LIKED) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (ID) DO NOTHING"
        movies_list = []
        for movie in json_response['Search']:
            record_to_insert = (movie['imdbID'], movie['Title'], movie['Year'], movie['Poster'], False)
            cursor.execute(insert_query, record_to_insert)
            connection.commit()
            movie['liked'] = False 
            movies_list.append(movie)
        results_response = { "Results": movies_list, "Pages": no_of_pages }
        return results_response
    except (Exception, psycopg2.Error) as error:
        print("An error has occured while searching for a movie title.", error)
        err_response = { "error msg": error }
        return err_response
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()

@bp.route('/movie_details', methods=['GET'])
def movie_details():
    try:
        connection = None
        connection = psycopg2.connect(DB_CONFIG)
        cursor = connection.cursor()
        query = request.args['id']
        response = requests.request("GET", BASE_URL + '&i=' + query)
        json_response = response.json()
        return json_response
    except (Exception, psycopg2.Error) as error:
        print("An error has occured while getting the movie details.", error)
        err_response = { "error msg": error }
        return err_response
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()

@bp.route('/like_movie', methods=['POST'])
def like_movie():
    try:
        connection = psycopg2.connect(DB_CONFIG)
        cursor = connection.cursor()
        movie_id = request.args['id']
        postgres_update_query = "UPDATE movies SET liked = %s WHERE id = %s"
        cursor.execute(postgres_update_query, ("true", movie_id))
        connection.commit()
        print("Record updated successfully into movies table")
        return Response(status=200)
    except (Exception, psycopg2.Error) as error:
        print("An error has occured while update movie status.", error)
        err_response = { "error msg": error }
        return err_response
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()

@bp.route('/unlike_movie', methods=['POST'])
def unlike_movie():
    try:
        connection = psycopg2.connect(DB_CONFIG)
        cursor = connection.cursor()
        movie_id = request.args['id']
        postgres_update_query = "UPDATE movies SET liked = %s WHERE id = %s"
        cursor.execute(postgres_update_query, ("false", movie_id))
        connection.commit()
        print("Record updated successfully into movies table")
        return Response(status=200)
    except (Exception, psycopg2.Error) as error:
        print("An error has occured while update movie status.", error)
        err_response = { "error msg": error }
        return err_response
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()

@bp.route('/get_liked_movies', methods=['GET'])
def get_liked_movies():
    try:
        connection = psycopg2.connect(DB_CONFIG)
        cursor = connection.cursor()
        select_query = "SELECT * FROM movies WHERE liked = true"
        cursor.execute(select_query)
        connection.commit()
        movies_list = []
        movie_db = cursor.fetchall()
        for movie in movie_db:
            movie_dict = {}
            movie_dict["imdbID"] = movie[0]
            movie_dict["Title"] = movie[1]
            movie_dict["Year"] = movie[2]
            movie_dict["Liked"] = movie[3]
            movie_dict["Poster"] = movie[4]
            movies_list.append(movie_dict)
        results_response = { "Results": movies_list }
        return results_response
    except (Exception, psycopg2.Error) as error:
        print("An error has occured while update movie status.", error)
        err_response = { "error msg": error }
        return err_response
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
