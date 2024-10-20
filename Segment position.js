//(function(){}()は即時関数（メリット：変数がlocalなので他のスクリプトと干渉しない。）
(function() {
	//csvを読み込む関数を定義
	var CreateSegPosition = function() {

		this.fileData = [];//txtファイルのデータ格納用
        this.itemNumber = app.activeDocument.pathItems.length; //アクティブドキュメント内のオブジェクトの種類がalertで返ってきた。ここでは、~.lengthで、パスアイテムの数を表示。
		this.data = []; //アートボード上の各pathItemデータ格納用

	};

	CreateSegPosition.prototype = {//プロトタイプはクラス継代のようなもの
		//: function()はメソッド（変数がローカルになる。method間での変数干渉防止措置)
		makefileData: function() {

			try {
				for(var i = 0, n = this.itemNumber; i < n; i++){
					this.data = app.activeDocument.pathItems[i];
					this.data.selected = true;

					for(var j = 0, k = this.data.pathPoints.length; j < k; j++){

						this.fileData.push('\n' + "seg_" + i + "path_" + j);
						this.fileData.push(app.activeDocument.pathItems[i].pathPoints[j].anchor[0]);//anchor[0]:x座標　anchor[1]:y座標（yはイラレ上の値と反転しているので、-1を乗算しないと一致しない。
						this.fileData.push(-(app.activeDocument.pathItems[i].pathPoints[j].anchor[1]));//anchor[0]:x座標　anchor[1]:y座標（yはイラレ上の値と反転しているので、-1を乗算しないと一致しない。

					}
				}

			} catch (e) {
				alert("error 01:failed to write anchor position to txt files." +'\n'+ "データ書き込み失敗")
			}
			
		},

		writetextF: function() {

            try {
            var path = Folder.selectDialog("Please select the saved dilectory. " +'\n'+ "txtファイル保存場所を選択");
			
            if (! path) {
            return;
            }
			
            var csv = new File(path +"/segposition.txt");
    
            if (! csv.open("w")) { //開けなかったら何もせずメソッド終了
                return;
            }
        
            csv.open('w'); //書き込み専用で開く				
            csv.write(this.fileData);//書き込む内容
            csv.close();

            alert("Success in writing text data to txt file." +'\n'+ " テキストデータ書き込み成功");
        } catch (e) {
            alert("error 02: failed to writing created data to txt file." +'\n'+ " テキストデータ生成失敗");
        }

        }

	};

	var creater = new CreateSegPosition();// インスタンス生成　creating instance
	creater.makefileData();//データ生成　creating data for writing to txt file.
	creater.writetextF();//テキストファイルに書き込み Writing created data to txt file.

})();