package com.moongate.bantatc;

import android.graphics.Color;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.LinearLayout;
import android.widget.Spinner;
import java.util.ArrayList;
import org.achartengine.ChartFactory;
import org.achartengine.GraphicalView;
import org.achartengine.model.CategorySeries;
import org.achartengine.renderer.DefaultRenderer;
import org.achartengine.renderer.SimpleSeriesRenderer;

public class Graficos extends BaseReport{
	public Spinner sp;
	private GraphicalView mChartView;
	private CategorySeries mSeries = new CategorySeries("");
  private DefaultRenderer mRenderer = new DefaultRenderer();
	private static int[] COLORS = new int[] { 
		Color.rgb(204, 212, 255),
		
		Color.rgb(255, 0, 128),
		Color.rgb(170, 255, 0),
		Color.rgb(255, 204, 212), 
		Color.rgb(212, 255, 204),
		Color.rgb(255, 212, 204),
		Color.rgb(0, 170, 255),
		Color.rgb(255, 0, 170),
		Color.rgb(0, 255, 170),
		Color.rgb(255, 255, 90),
		Color.GREEN, Color.BLUE, Color.MAGENTA, Color.CYAN, Color.RED, 
		Color.YELLOW 
	};
	
	@Override
	public void onCreate(Bundle icicle) {
	  super.onCreate(icicle, R.layout.graficos);
		//chart
		if (mRenderer != null){
		
			mRenderer.setApplyBackgroundColor(true);
			mRenderer.setBackgroundColor(Color.argb(100, 30, 30, 30));
			mRenderer.setChartTitleTextSize(20);
			mRenderer.setLabelsTextSize(15);
			mRenderer.setLegendTextSize(15);
			mRenderer.setMargins(new int[] { 0, 0, 0, 0 });
			mRenderer.setZoomButtonsVisible(true);
			mRenderer.setStartAngle(90);
			
			LinearLayout layout = (LinearLayout) findViewById(R.id.chart);
			mChartView = ChartFactory.getPieChartView(this, mSeries, mRenderer);
			layout.addView(mChartView, new ViewGroup.LayoutParams(ViewGroup.LayoutParams.FILL_PARENT,
						ViewGroup.LayoutParams.FILL_PARENT));
		}
	
		//chart end
		sp = (Spinner)findViewById(R.id.C_box);
		sp.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
			public void onItemSelected(AdapterView<?> parent, View view, int pos, long id) { 
				 Graficos.this.report_type = pos;
	    } 

		  public void onNothingSelected(AdapterView<?> adapterView) {
			    return;
			} 
		}); 
	 }	
	@Override
	public void mostrarReporte(wsReports.InstanciaReporte results){
		mSeries.clear();
		int count = 0;
		int idx_tag = results.idx_tag;
		int idx_val = results.idx_val;
		
		//mostramos solo los 10 primeros
		int len  = results.rows.size();
		if (len>10){
			len = 10;
		}
		
		for (int i = 0; (i<len); i++){
			ArrayList<String> row = results.rows.get(i);
		
			String k = row.get(idx_tag);
			double val = Double.valueOf(row.get(idx_val));
			mSeries.add(k, val);
			
			SimpleSeriesRenderer renderer = new SimpleSeriesRenderer();
			renderer.setColor(COLORS[count]);
			mRenderer.addSeriesRenderer(renderer);
			//si, mucho menos elegante pero 10 veces mas rapido que el mod
			count++;
			if (count >= COLORS.length){
				count=0;
			}
		}
		mChartView.repaint();
	}
	@Override
    protected void onResume() {
        super.onResume();

        if(mChartView!=null){
            mChartView.repaint();
        }

    }
}
