import { Component, OnInit } from '@angular/core';
import { ngxCsv } from 'ngx-csv/ngx-csv';
import { ActivatedRoute } from '@angular/router';

import { BackendService } from '../backend.service';
import { Measurement } from '../classes/measurement';
import { RhValue } from '../classes/rh-value';
import { PaginatedList } from '../classes/paginated-list';

import { Color } from 'ng2-charts';
import { SpeedPipe } from '../pipe/speed.pipe';
import { MobilityPipe } from '../pipe/mobility.pipe';
import { SheetResistancePipe } from '../pipe/sheet-resistance.pipe';

@Component({
  selector: 'app-details',
  templateUrl: './details.component.html',
  styleUrls: ['./details.component.css'],
})
export class DetailsComponent implements OnInit {
  measurement: Measurement;
  rhValue: PaginatedList<RhValue>;
  id: number;

  chartOptions = {
    responsive: true,
    scales: {
      yAxes: [
        {
          scaleLabel: {
            display: true,
            labelString: 'Rh [Ohm]',
          },
        },
      ],
      xAxes: [
        {
          scaleLabel: {
            display: true,
            labelString: 'Angle [degree]',
          },
        },
      ],
    },
  };
  chartData = [{ data: [0], label: '' }];
  chartLabels = [0];

  lineChartColors: Color[] = [
    {
      // red
      backgroundColor: 'rgba(0,0,0,0)',
      borderColor: 'red',
      pointBackgroundColor: 'rgba(255,0,0,1)',
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: 'rgba(255,0,0,0.8)',
    },
    {
      // blue
      backgroundColor: 'rgba(0,0,0,0)',
      borderColor: 'blue',
      pointBackgroundColor: 'blue',
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: 'blue',
    },
  ];

  constructor(
    private route: ActivatedRoute,
    private backend: BackendService,
    private speed: SpeedPipe,
    private mobility: MobilityPipe,
    private sheetResistance: SheetResistancePipe
  ) {}

  ngOnInit(): void {
    this.id = +this.route.snapshot.paramMap.get('id');
    this.getMeasurement();
    this.getRhValues();
  }

  getMeasurement(): void {
    this.backend
      .get_measurement(this.id)
      .subscribe((measurement: Measurement) => {
        this.measurement = measurement;
      });
  }

  getRhValues(): void {
    const request = this.backend.get_rh_values_for_measurement(this.id);
    request.subscribe((rhValue: PaginatedList<RhValue>) => {
      this.rhValue = rhValue;
      this.chartLabels = this.rhValue.results.map(i => i.angle);
      this.chartData = [
        { data: this.rhValue.results.map(v => v.value), label: 'Rh' },
        { data: this.getFittedCurve(), label: 'Fitted Curve' },
      ];
    });
  }

  getFittedCurve() {
    const fit = [...Array(360).fill(0)];
    for(let i=0; i<360; i++) {
      fit[i] = 
        this.measurement.amplitude * 
          Math.sin(this.measurement.angle_freq * i + this.measurement.phase) +
        this.measurement.offset;
    }
    return fit;
  }

  download_image() {
    const canvas = document.getElementsByTagName('canvas')[0].toDataURL();
    const link = document.createElement('a');
    link.download = this.measurement.name;
    link.href = canvas;
    link.click();
  }

  downloadCsv() {
    let measurementData: any[] = [
      { name: 'Name:', measurementName: this.measurement.name },
      { name: 'Measurement id:', measurement_id: this.measurement.id },
      { name: 'Created at:', created_at: this.measurement.created_at },
      { name: 'Description:', description: this.measurement.description },
      {
        name: 'Speed:',
        speed: this.speed.transform(this.measurement.steps_per_measurement),
      },
      { name: 'Current limit [A]:', current_limit: this.measurement.current_limit },
      {
        name: 'Connections:',
        connection_1: this.measurement.connection_1,
        connection_2: this.measurement.connection_2,
        connection_3: this.measurement.connection_3,
        connection_4: this.measurement.connection_4,
      },
      {
        name: 'Mobility [cm^2/(Vs)]:',
        mobility: this.mobility.transform(this.measurement.mobility),
      },
      {
        name: 'Sheet Resistans [Ohm]:',
        sheet_resistanse: this.sheetResistance.transform(
          this.measurement.sheet_resistance
        ),
      },
      {},
      { name: 'Parameters of the Fitted Curve' },
      { name: 'Amplitude:', amplitude: this.measurement.amplitude },
      { name: 'Angle frequency:', angle_freq: this.measurement.angle_freq },
      { name: 'Phase:', phase: this.measurement.phase },
      { name: 'Offset', offset: this.measurement.offset },
    ];
    const datarhValue = this.rhValue.results.map(obj => {
      return {
        id: obj.angle,
        value: obj.value,
      };
    });
    const dataLabels = [
      { name: '', name2: '' },
      { name: 'Angle', name2: 'Rh Value' },
    ];
    measurementData = measurementData.concat(dataLabels).concat(datarhValue);
    const options = {
      fieldSeparator: ';',
      quoteStrings: '"',
      decimalseparator: '.',
      showLabels: true,
      showTitle: true,
      title: '',
      useBom: false,
      noDownload: false,
      headers: [],
    };
    new ngxCsv(measurementData, this.measurement.name, options);
  }
}
