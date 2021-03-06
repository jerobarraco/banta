/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package com.moongate.bantatc;

import android.util.Log;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;

import org.apache.http.HttpEntity;
import org.apache.http.conn.ConnectTimeoutException;
import org.apache.http.HttpResponse;
import org.apache.http.StatusLine;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpUriRequest;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.params.BasicHttpParams;
import org.apache.http.params.HttpConnectionParams;
import org.apache.http.params.HttpParams;
import org.json.JSONObject;


/**
 * Clase base para realizar comunaciones al webservice... 
 
 * @author MoonGate
 */
//TODO usar esta clase en los otros WS
//TODO poner un authenticator acá

public class wsBase {
	//Estas dos variables permiten verificar el resultado de la operacion y si hay algun error
	public String error = "";
	public boolean success = false;
	HttpClient client;
                private String myEncAuth ="";//string de autenticacion
	class WSException extends Exception{
		String m;
		WSException (String msg){
			super(msg);
			this.m = msg;
		}
		@Override
		public String toString(){
			return this.m;
		}
	}
	//Constructor sobrecargado para poder testear un user o password o usar un user/pass diferente en un webservice especifico
	//si se crea un wsBase sin parametros entonces utilizara el user/pass guardado en las preferencias
	public wsBase(String user, String pwd){ 
		//generamos un encAuth a partir del pass y la contraseña
		//el password debe estar encodeado con Pref.encodePassword!! (ojo)
		
		myEncAuth = Pref.genEncAuth(user, pwd);
		//muy importante, ponerle utf8
		//le ponemos al cliente que agregue el parametro utf

		final HttpParams httpParams = new BasicHttpParams();
		HttpConnectionParams.setConnectionTimeout(httpParams, 10000);
		client = new DefaultHttpClient(httpParams);
		client.getParams().setParameter("http.protocol.content-charset", "UTF-8");
		client.getParams().setParameter("http.useragent", "BantaTC");
	}
	public wsBase(){
		//lo que hacemos es que cuando creamos un wsBase sin parametros, tomamos la identificacion de las preferencias
		//llamamos al constructor con user y password de las preferencias
		this(Pref.user, Pref.pwd);
	}
	public JSONObject doRequest(HttpUriRequest req){
		//ponemos la autenticacion para el user y passwd
		req.setHeader("Authorization", myEncAuth);
		JSONObject res = null;
		this.error = "";
		this.success = false;
		try{		
			HttpResponse response = client.execute(req);
			res = this.getJSON(response);
			this.success = true;

		}        catch (ClientProtocolException e) {
				this.error = e.toString();
				Log.e(wsBase.class.toString(), this.error);
		} catch (org.apache.http.conn.ConnectTimeoutException e ) {
				this.error ="La conexión superó el tiempo máximo, revise la conexión con Banta";
				Log.e(wsBase.class.toString(), e.toString());
		} catch (java.lang.IllegalArgumentException e){
			this.error = "Configure primero la dirección del servidor";
			Log.e(wsBase.class.toString(), e.toString());
		} catch (java.net.SocketException e){
			this.error = "No pudo establecer la conexión a internet";
			Log.e(wsBase.class.toString(), e.toString());
		}catch (Exception e){
				this.error = e.toString();
				Log.e(wsBase.class.toString(), this.error);
			}
			return res;
		}
	public JSONObject getJSON(HttpResponse response) throws Exception{
		//esta funcion puede ser util afuera, y no utiliza variables de instancia
		//asi que puede ser puesta publica
		//aunque la idea es usar doRequest
		StatusLine stat = response.getStatusLine();
		StringBuilder sb = new StringBuilder();
		JSONObject responseObj;
		String err; 
		int statcode = stat.getStatusCode();
		if (statcode == 401){
			err = "Usuario y/o contraseña incorrectos.";
			throw new WSException (err);
		}else if (statcode != 200){
			err = "Error en servidor.";
			throw new WSException (err);
		}
		HttpEntity entity = response.getEntity();
		InputStream content = entity.getContent();
		BufferedReader reader = new BufferedReader(new InputStreamReader(content));
		String line;
		while ( (line=reader.readLine()) != null){
			sb.append(line);
		}
		responseObj = new JSONObject(sb.toString());
		boolean lc_success = responseObj.getBoolean("success");
		if (!lc_success){
			err = "Error en servidor: " + responseObj.getString("error");
			throw new WSException(err);
		}
		return responseObj;
	}
}
