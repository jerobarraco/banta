package com.moongate.bantatc;

import android.net.Uri;
import android.os.AsyncTask;
import android.util.Log;
import android.widget.Toast;
import java.util.ArrayList;
import org.apache.http.client.methods.HttpGet;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

public class wsReports extends AsyncTask<BaseReport, Void, wsReports.InstanciaReporte> {

	private BaseReport padre;
	private wsBase ws = new wsBase();
	private final static String[] tipos = {
		"product", "client", "category", "user", "move", "buy"
	};
	//Clase interna para permitir el pasaje de datos del reporte
	//lo necesitamos porque el reporte es una estructura compleja
	public class InstanciaReporte{
		//Indica si hubo un error
		public String error;
		//indica si todo salio bien
		public boolean success;
		//indices (columnas) para la version grafica
		//tag es el "label" , val el valor a mostrar
		public int idx_tag, idx_val;
		//headers
		public ArrayList<String> heads;
		//filas
		public ArrayList<ArrayList<String>> rows;
		public InstanciaReporte(){
			this.error = "";
			this.success = false;
			idx_tag = 0;
			idx_val = 0;
			//inicializamos los otros arraylists porque es mas eficiente inicalizarlso con el tamaño
			//hay q tener cuidado, de no inicializarlos seran null
		}
	}
	@Override
	protected InstanciaReporte doInBackground(BaseReport... class_padre) {

		this.padre = class_padre[0];

		//Generamos el query
		Uri.Builder b = Uri.parse("http://"+Pref.ip+":8080").buildUpon();
		b.path("/reports");
		if (this.padre.report_type >= tipos.length){
			this.ws.error = "Reporte incorrecto";
			this.ws.success = false;
			return null;
		}
		b.appendQueryParameter("type", tipos[this.padre.report_type]);
		String url = b.build().toString();

		HttpGet httpGet = new HttpGet(url);
			
		JSONObject res = ws.doRequest(httpGet);
		return decodeJSON(res);
	}
	
	private InstanciaReporte decodeJSON(JSONObject r){
		InstanciaReporte res = new InstanciaReporte();
		if (!this.ws.success){
			res.success = false;
			res.error = this.ws.error;
			return res;
		}
		try {
			//obtenemos los headers
			JSONArray jtemp = r.getJSONArray("headers");
			int k = jtemp.length();
			//al tener el tamaño es mas eficiente
			res.heads = new ArrayList<String>(k);
			//convertimos el ArrayJSon HEADERS a ArrayString
			for (int i = 0; i<k; i++){
				res.heads.add(jtemp.getString(i));
			}
			//ahora con los tags (indices para los graficos)
			res.idx_tag = r.getInt("idx_tag");
			res.idx_val = r.getInt("idx_val");
			
			JSONArray rows = r.getJSONArray("data");
			k = rows.length();
			res.rows = new ArrayList<ArrayList<String>>(k);
			
			for (int i=0; i<k; i++){
				//get the country information JSON object
				 JSONArray fila = rows.getJSONArray(i);
				//create java object from the JSON object
				 int z = fila.length();
				 ArrayList<String> celdas = new ArrayList<String>(z);

				 for (int j=0; j<z; j++) {
					 celdas.add(fila.getString(j));
				 }
				res.rows.add(celdas);
			}
			res.success = true;
		} catch (JSONException ex) {
			res.success = false;
			res.error = "Error. " + ex.toString();
			Log.e(wsReports.class.toString(), res.error);
		}
		return res;
	}
	@Override
	public void onPostExecute(InstanciaReporte rep){
		if (rep.success){
			if (rep.rows.size()==0){
				Toast.makeText( this.padre, "No hay datos que mostrar en este mes.", Toast.LENGTH_LONG).show();
			}
			this.padre.mostrarReporte(rep);
		}else{
			Toast.makeText(this.padre, this.ws.error, Toast.LENGTH_LONG).show();
		}
	}
}

