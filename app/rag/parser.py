import werkzeug
from flask_restx import reqparse
from werkzeug.datastructures import FileStorage

multiple_files_upload_parser = reqparse.RequestParser()
multiple_files_upload_parser.add_argument('files', location='files', type=FileStorage, required=True, action='append')

question_parser = reqparse.RequestParser(bundle_errors=True)
question_parser.add_argument(
    'question',
    required=True,
    type=str,
    location='form')


task_id_parser = reqparse.RequestParser()
task_id_parser.add_argument('task_id', type=str, required=True, help='A required string parameter')

