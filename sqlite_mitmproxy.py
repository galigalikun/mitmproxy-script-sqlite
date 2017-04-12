# -*- coding: utf-8 -*-

from mitmproxy.utils import human
import os
import argparse
import sqlite3

class Writer:
    def __init__(self, dbname):
        if os.path.isfile(dbname):
            os.remove(dbname)

        self.conn = sqlite3.connect(dbname)
        self.c = self.conn.cursor()

        create_table = '''create table mitmproxy (id int, timestamp_start datetime, timestamp_end datetime,
                          method varchar(32), url varchar(255), status_code int, request varchar(255), response varchar(255), detail varchar(255))'''
        self.c.execute(create_table)
    def request(self, flow):
        print(flow.request.headers["User-Agent"])
#        flow.request.headers["User-Agent"] = "ccc"

    def response(self, flow):
        sql = 'insert into mitmproxy (timestamp_start, timestamp_end, method, url, status_code, request, response, detail) values (?, ?, ?, ?, ?, ?, ?, ?)'
        request = ""
        response = ""
        for key, value in flow.request.headers.items():
            request += " {0} : {1} \n".format(key, value)
        for key, value in flow.response.headers.items():
            response += " {0} : {1} \n".format(key, value)

        request += "\n{0}".format(flow.request.content)
        response += "\n{0}".format(flow.response.content)
        param = (flow.request.timestamp_start, flow.request.timestamp_end, flow.request.method, flow.request.url, flow.response.status_code, request, response, self.detail(flow))
        print(sql)
        self.c.execute(sql, param)
        self.conn.commit()

    def detail(self, flow):
        if flow.response.raw_content:
            details = "{}, {}".format(
                flow.response.headers.get("content-type", "unknown content type"),
                human.pretty_size(len(flow.response.raw_content))
            )
        else:
            details = "no content"
        return "Response({status_code} {reason}, {details})".format(
            status_code=flow.response.status_code,
            reason=flow.response.reason,
            details=details
        )

def start():
    parser = argparse.ArgumentParser()
    parser.add_argument("dbname", type=str)
    args = parser.parse_args()
    return Writer(args.dbname)
