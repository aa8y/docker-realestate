from flask import Flask, abort, jsonify, request
from homeharvest import scrape_property
from marshmallow import Schema, ValidationError, fields, validate
from os import environ

app = Flask(__name__)
port = int(environ.get('PORT', 5000))

class SearchRequestSchema(Schema):
  location = fields.Str(required=True)
  listing_type = fields.Str(
    load_default='for_sale', 
    required=False, 
    validate=validate.OneOf(['for_sale', 'for_rent', 'pending', 'sold'])
  )
  radius = fields.Float(required=False)
  mls_only = fields.Bool(required=False)
  past_days = fields.Int(required=False)
  proxy = fields.Str(required=False)
  from_date = fields.Date(required=False)
  to_date = fields.Date(required=False)
  include_foreclosed = fields.Bool(required=False)
  fetch_additional_data = fields.Bool(required=False)
  exclude_pending = fields.Bool(required=False)

@app.route('/health', methods=['GET'])
def health_check():
  try:
    result_df = scrape_property(
      location = 'Redmond, WA',
      extra_property_data = False
    )
    if (result_df.size == 0):
      return jsonify({'status': 'error'}), 400
    return jsonify({'status': 'ok'}), 200
  except err:
    return jsonify({'status': 'error'}), 500
  return jsonify({'status': 'ok'}), 200

@app.route('/search', methods=['POST'])
def search():
  json_data = request.get_json()
  if not json_data:
    return jsonify({'message': 'No input data provided'}), 400

  request_schema = SearchRequestSchema()
  try:
    data = request_schema.load(json_data)
    result_df = scrape_property(
      location = data['location'],
      listing_type = data['listing_type'],
      radius = data.get('radius'),
      mls_only = data.get('mls_only', False),
      past_days = data.get('past_days'),
      date_from = data.get('from_date'),
      date_to = data.get('to_date'),
      foreclosure = data.get('include_foreclosed'),
      extra_property_data = data.get('fetch_additional_data', True),
      exclude_pending = data.get('exclude_pending')
    )
    result = result_df.to_json(orient='records')
    return result, 200
  except ValidationError as err:
    return jsonify(err.messages), 422

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=port)
