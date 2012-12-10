/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package com.moongate.bantatc;

import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.Spinner;
import java.util.ArrayList;

public class Reportes extends BaseReport {
	public ListView lv;
	public Spinner sp;
	@Override
	public void onCreate(Bundle icicle) {
	  super.onCreate(icicle, R.layout.reportes);
		sp = (Spinner) findViewById(R.id.rep_c_box);
		lv = (ListView) findViewById(R.id.rep_lv);
		sp.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
			public void onItemSelected(AdapterView<?> parent, View view, int pos, long id) { 
				 Reportes.this.report_type = pos;
	    } 

		  public void onNothingSelected(AdapterView<?> adapterView) {
			    return;
			} 
		}); 
	}
	
	@Override
	public void mostrarReporte( wsReports.InstanciaReporte rep) {
		ArrayList<String> heads = rep.heads; //es una copia de referencia, sin costo
		ArrayList<String> items  = new ArrayList(rep.rows.size());
	
		for(ArrayList<String> r: rep.rows ){
			//formatear es muy costoso aca
			String row="";
			
			for (int i = 0; i< r.size(); i++){
				//aunque concatenar no es gratis
				row += heads.get(i) + ": "+r.get(i)+"\n";
			}
			
			items.add(row);
		}
		ArrayAdapter a = new ArrayAdapter<String>(this, android.R.layout.simple_list_item_1, items );
		this.lv.setAdapter(a);
	}
	
	
}
