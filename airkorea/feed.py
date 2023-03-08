"""
한국환경공단의 Air Korea 데이터를 받아서
한국에스리 포털에 있는 대기오염 정보를 업데이트 한다.
"""

import requests
import os
import logging
import pandas as pd

from copy import deepcopy
from dotenv import load_dotenv
from datetime import datetime
from arcgis.gis import GIS
from arcgis.features import (
    GeoAccessor,
    GeoSeriesAccessor,
    FeatureLayer,
    FeatureLayerCollection,
)
from pathlib import Path

# 환경변수를 읽어온다
load_dotenv()


def call_api_data() -> requests.Response:
    """
    미세먼지 API 관련해서 필요한 endpoint는 시도별 데이터다.
    에어코리아 API의 시도별 endpoint를 호출하여 받은 response를 반환한다
    """
    URL = os.getenv("AQI_URL")
    KEY = os.getenv("DATAGOKR_KEY")
    if URL is None or KEY is None:
        raise EnvironmentError("Could not read environment values.")
    response = requests.get(
        url="/".join([URL, "getCtprvnRltmMesureDnsty"]),
        params={
            "serviceKey": KEY,
            "returnType": "json",
            "numOfRows": 1000,
            "pageNo": 1,
            "sidoName": "전국",
            "ver": 1.0,
        },
    )
    if response.status_code != 200:
        raise RuntimeError("Failed to fetch API. Check network.")
    return response


def connect_to_agol() -> GIS:
    """한국에스리 포털에 연결하고, 연결된 포털을 반환한다."""
    gis = GIS(
        url="https://portal.esrikr.com/portal",
        username=os.getenv("ESRI_USER"),
        password=os.getenv("ESRI_PW"),
    )
    return gis


def get_feature_layer_col(flc_title="KoreaAirQuality") -> FeatureLayerCollection:
    """
    한국에스리 포털에 접속해서 내가 만든 미세먼지 피쳐 레이어 콜렉션을
    반환한다.
    """
    gis = connect_to_agol()  # 한국에스리 포털

    # Air Quality Feature Layer Collection
    aqi_flc = gis.content.search(
        query=f"owner:{gis.users.me.username} AND title:{flc_title}",
        item_type="Feature Layer Collection",
    )
    if len(aqi_flc) == 0:
        raise RuntimeError("Could not find the layer. Check query.")
    return aqi_flc[0]


def read_to_be_updated_fields(filename: str = "to_be_updated_fields.txt") -> list:
    """변경해야 하는 필드명을 읽고 리스트로 반환한다"""
    with open(filename, "r", encoding="utf-8") as f:
        fields = [field.strip() for field in f.readlines()]
    return fields


def get_station_names(filename: str = "station_names.txt") -> list:
    """
    에어코리아의 측정소명을 모두 읽고 리스트로 반환한다.
    이 측정소명은 추후 작업에서 조인-키 로 사용한다
    """
    with open(filename, "r", encoding="utf-8") as f:
        station_names = [name.strip() for name in f.readlines()]
    return station_names


def build_update_features() -> list:
    """gis.edit_features에 넘길 업데이트 내용을 구성한다"""
    features_to_be_updated = []
    update_fields = read_to_be_updated_fields()

    # air quality feature layer collection
    flc = get_feature_layer_col().layers[0]
    all_features = flc.query().features

    new_data = pd.DataFrame(call_api_data().json()["response"]["body"]["items"])

    # names of all stations used by AirKorea
    station_names = get_station_names()

    for station in station_names:
        # print(all_features[0].attributes.keys())
        original_feature = [
            f for f in all_features if f.attributes["stationName".lower()] == station
        ][0]
        print(str(original_feature))

        # feature from agol
        update_feature = deepcopy(original_feature)
        # print(str(update_feature))
        # feature from api
        matching_row = new_data.loc[new_data["stationName"] == station]

        # update_feature.attributes["datatime"] = matching_row["dataTime"].iloc[0]
        # update_feature.attributes["so2value"] = matching_row["so2Value"].iloc[0]
        # update_feature.attributes["so2grade"] = matching_row["so2Grade"].iloc[0]
        # update_feature.attributes["so2flag"] = matching_row["so2Flag"].iloc[0]
        # update_feature.attributes["o3grade"] = matching_row["o3Grade"].iloc[0]
        # update_feature.attributes["o3value"] = matching_row["o3Value"].iloc[0]
        # update_feature.attributes["o3flag"] = matching_row["o3Flag"].iloc[0]
        # update_feature.attributes["pm25grade"] = matching_row["pm25Grade"].iloc[0]
        # update_feature.attributes["pm25flag"] = matching_row["pm25Flag"].iloc[0]
        # update_feature.attributes["pm25value"] = matching_row["pm25Value"].iloc[0]
        # update_feature.attributes["pm10flag"] = matching_row["pm10Flag"].iloc[0]
        # update_feature.attributes["pm10value"] = matching_row["pm10Value"].iloc[0]
        # update_feature.attributes["pm10grade"] = matching_row["pm10Grade"].iloc[0]
        # update_feature.attributes["no2value"] = matching_row["no2Value"].iloc[0]
        # update_feature.attributes["no2grade"] = matching_row["no2Grade"].iloc[0]
        # update_feature.attributes["no2flag"] = matching_row["no2Flag"].iloc[0]
        # update_feature.attributes["coflag"] = matching_row["coFlag"].iloc[0]
        # update_feature.attributes["covalue"] = matching_row["coValue"].iloc[0]
        # update_feature.attributes["cograde"] = matching_row["coGrade"].iloc[0]
        # update_feature.attributes["khaivalue"] = matching_row["khaiValue"].iloc[0]
        # update_feature.attributes["khaigrade"] = matching_row["khaiGrade"].iloc[0]

        for field in update_fields:
            update_feature.attributes[field.lower()] = matching_row[field].iloc[0]

        features_to_be_updated.append(update_feature)
        # print(str(update_feature))
        # print("-" * 40)

    return features_to_be_updated


def do_edit() -> bool:
    """
    지금까지 만든 작업을 한번에 다 호출해서 최종 편집
    """
    updates = build_update_features()
    layer = get_feature_layer_col("KoreaAirQuality").layers[0]
    layer.edit_features(updates=updates)
    return True


if __name__ == "__main__":
    do_edit()
