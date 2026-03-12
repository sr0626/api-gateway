import json
import datetime
import boto3
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    ts = datetime.datetime.utcnow().isoformat() + "Z"
    request_id = getattr(context, "aws_request_id", None)
    payload = event.get("detail", event)

    # Minimal debug info
    event_summary = payload if isinstance(payload, dict) and len(json.dumps(payload)) < 2000 else str(type(payload))

    path_params = event.get("pathParameters") or {}
    query_params = event.get("queryStringParameters") or {}
    # when using {proxy+} the path param key is typically 'proxy'
    proxy_path = path_params.get("proxy") if isinstance(path_params, dict) else None

    # concise log for CloudWatch
    log = {"timestamp": ts, "request_id": request_id, "proxy_path": proxy_path, "query": query_params}
    print(json.dumps(log, separators=(',', ':'), ensure_ascii=False))

    # Determine bucket name: prefer explicit query param `bucket`, else first path segment
    bucket = None
    if isinstance(query_params, dict) and query_params.get("bucket"):
        bucket = query_params.get("bucket")
    elif proxy_path:
        # proxy_path may include multiple segments; take first segment as bucket name
        bucket = proxy_path.split("/")[0]

    if not bucket:
        resp = {"statusCode": 400, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": "missing bucket name (pass ?bucket=name or /<bucket> in path)"})}
        return resp

    # optional max items query parameter
    max_items = 1000
    if isinstance(query_params, dict) and query_params.get("max"):
        try:
            max_items = int(query_params.get("max"))
        except Exception:
            pass

    # determine whether to perform recursive listing
    recursive_flag = False
    if isinstance(query_params, dict) and query_params.get("recursive"):
        rv = str(query_params.get("recursive")).lower()
        if rv in ("1", "true", "yes"):
            recursive_flag = True

    try:
        if recursive_flag:
            items, truncated = list_s3_objects(bucket, max_items=max_items)
        else:
            items, truncated = list_s3_objects_nonrecursive(bucket, max_items=max_items)
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        msg = e.response.get("Error", {}).get("Message")
        resp = {"statusCode": 500, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": code, "message": msg})}
        return resp

    resp_body = {"ok": True, "bucket": bucket, "count": len(items), "objects": items, "truncated": truncated, "recursive": recursive_flag}
    response = {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps(resp_body)}
    return response

def list_s3_objects(bucket, max_items=1000):
    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket)

    items = []
    try:
        for page in page_iterator:
            contents = page.get('Contents', [])
            for o in contents:
                items.append({
                    'Key': o.get('Key'),
                    'Size': o.get('Size'),
                    'LastModified': o.get('LastModified').isoformat() if o.get('LastModified') else None
                })
                if len(items) >= max_items:
                    return items, True
        return items, False
    except ClientError as e:
        raise


def list_s3_objects_nonrecursive(bucket, prefix='', max_items=1000):
    """List only the top-level objects and prefixes in a bucket (non-recursive).
    Uses Delimiter='/' to get common prefixes (pseudo-directories) and top-level objects.
    Returns (items, truncated).
    """
    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket, Delimiter='/', Prefix=prefix)

    items = []
    try:
        for page in page_iterator:
            for o in page.get('Contents', []):
                items.append({
                    'Key': o.get('Key'),
                    'Size': o.get('Size'),
                    'LastModified': o.get('LastModified').isoformat() if o.get('LastModified') else None
                })
                if len(items) >= max_items:
                    return items, True
            for cp in page.get('CommonPrefixes', []):
                items.append({'Prefix': cp.get('Prefix')})
                if len(items) >= max_items:
                    return items, True
        return items, False
    except ClientError:
        raise
