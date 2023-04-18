# anti-pattern

## Api

### scan

获取所有扫描记录
`request_url:/scan`

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "res": [
      {
        "_key": "778783",
        "native": "aosp",
        "native_node": "android_11.0.0_r1",
        "extensive": "lineage",
        "extensive_node": "lineage18.1",
        "extensive_url": "111",
        "scan_time": "2023-04-10-16-39-04",
        "state": "running"
      }
    ],
    "count": 1
  }
}
```

### Anti-Pattern

#### 获取反模式信息及各种类数量

`request_url:/anti`

```json
{
  "scan_id": "778783",
  "module": "false",
  "file_path": ""
}
```

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "antis": [
      {
        "style": "add_parameter",
        "count": 53,
        "antis": [
          0,
          1,
          2,
          3,
          4,
          5,
          6
        ]
      }
    ]
  }
}
```

#### 获取文件级别反模式信息及各种类数量

`request_url:/anti`

```json
{
  "scan_id": "778783",
  "module": "false",
  "file_path": ""
}
```

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "file_set": [
      "packages/SystemUI/src/com/android/systemui/qs/QuickQSPanel.java",
      "packages/SystemUI/src/com/android/systemui/qs/tiles/AntiFlickerTile.java",
      "packages/SystemUI/src/com/android/systemui/qs/tileimpl/QSTileImpl.java"
    ],
    "antis": {
      "packages/SystemUI/src/com/android/systemui/qs/QuickQSPanel.java": [
        {
          "style": "add_parameter",
          "count": 53,
          "antis": [
            0,
            1,
            2,
            3,
            4,
            5,
            6
          ]
        }
      ]
    }
  }
}
```

#### 获取具体某一反模式信息

`request_url:/anti/<anti_id>`

```json
{
  "scan_id": "778783",
  "module": "false",
  "file_path": ""
}
```

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "antis": {
      "_key": "778891",
      "scan_id": "778783",
      "id": 10,
      "category": "IntrusiveModify",
      "style": "class_intrusive_add_method",
      "files": [
        "core/java/android/bluetooth/le/BluetoothLeScanner.java"
      ],
      "rels": [
        {
          "_key": "778783_235349",
          "id": 235349,
          "src": [
            {
              "_key": "778783_61179",
              "id": 61179,
              "category": "Class",
              "qualifiedName": "android.bluetooth.le.BluetoothLeScanner",
              "ownership": "intrusive native",
              "name": "BluetoothLeScanner",
              "commits_count": {
                "actively_native": 36,
                "obsolotely_native": 0,
                "extensive": 1
              },
              "file_path": "core/java/android/bluetooth/le/BluetoothLeScanner.java",
              "packageName": "android.bluetooth.le",
              "location": {
                "startLine": 41,
                "startColumn": 0,
                "endLine": 630,
                "endColumn": 0
              },
              "rawType": "android.bluetooth.le.BluetoothLeScanner",
              "modifiers": "public final",
              "intrusiveModify": {
                "class_body_modify": "-"
              },
              "scan_id": "778783"
            }
          ],
          "rel_type": "Define",
          "dest": [
            {
              "_key": "778783_61308",
              "id": 61308,
              "category": "Method",
              "qualifiedName": "android.bluetooth.le.BluetoothLeScanner.isRoutingAllowedForScan",
              "ownership": "extensive",
              "name": "isRoutingAllowedForScan",
              "commits_count": {
                "actively_native": 0,
                "obsolotely_native": 0,
                "extensive": 1
              },
              "file_path": "core/java/android/bluetooth/le/BluetoothLeScanner.java",
              "packageName": "android.bluetooth.le",
              "location": {
                "startLine": 621,
                "startColumn": 4,
                "endLine": 629,
                "endColumn": 4
              },
              "parameterTypes": "android.bluetooth.le.ScanSettings",
              "parameterNames": "settings",
              "rawType": "boolean",
              "modifiers": "private",
              "hidden": "blacklist",
              "scan_id": "778783"
            }
          ],
          "scan_id": "778783"
        }
      ]
    }
  }
}
```

### Get file text

`request: url:/entity/<entity_id>`

```json
{
  "scan_id": "778783"
}
```

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "entity": {
      "_key": "778783_235349",
      "_id": "entity/778783_235349",
      "_rev": "_f0nR2dS--i",
      "id": 235349,
      "category": "Variable",
      "qualifiedName": "android.widget.SlidingDrawer.mMaximumAcceleration",
      "ownership": "actively native",
      "name": "mMaximumAcceleration",
      "commits_count": {},
      "file_path": "core/java/android/widget/SlidingDrawer.java",
      "packageName": "android.widget",
      "location": {
        "startLine": 142,
        "startColumn": 22,
        "endLine": 142,
        "endColumn": 41
      },
      "rawType": "int",
      "modifiers": "private final",
      "global": true,
      "hidden": "greylist-max-o",
      "scan_id": "778783"
    },
    "file": "\n\nimport android.R;\nimport android.compat.annotation.UnsupportedAppUsage;\nimport android.content.Context;\nimport android.content.res.TypedArray;\nimport android.graphics.Bitmap;\nimport android.graphics.Canvas;\nimport android.graphics.Rect;\nimport android.os.SystemClock;"
  }
}
```