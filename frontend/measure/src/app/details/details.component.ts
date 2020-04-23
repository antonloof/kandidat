import { Component, OnInit, Input } from '@angular/core';
import { ngxCsv } from 'ngx-csv/ngx-csv';
import { ActivatedRoute } from '@angular/router';

import { BackendService } from '../backend.service';
import { Measurement } from '../classes/measurement';
import { RhValue } from '../classes/rh-value';
import { PaginatedList } from '../classes/paginated-list';

import { Color } from 'ng2-charts';

@Component({
  selector: 'app-details',
  templateUrl: './details.component.html',
  styleUrls: ['./details.component.css'],
})
export class DetailsComponent implements OnInit {
  measurement: Measurement;
  rhValue: PaginatedList<RhValue>;
  speed = '';
  measurementData = [];
  rhvalueData = [];
  measurementName = '';
  id = +this.route.snapshot.paramMap.get('id');

  constructor(private route: ActivatedRoute, private backend: BackendService) {}

  getMeasurement(): void {
    this.backend.get_measurement(this.id).subscribe((measurement: Measurement) => {
      if (measurement.steps_per_measurement === 20) {
        this.speed = 'High Speed : Low Resolution';
      } else if (measurement.steps_per_measurement === 10) {
        this.speed = 'Medium Speed : Medium Resolution';
      } else if (measurement.steps_per_measurement === 2) {
        this.speed = 'Low Speed : High Resolution';
      }
      this.measurementData = [
        { name1: 'Name:', name: measurement.name },
        { name1: 'Measurement id:', measurement_id: measurement.id },
        { name1: 'Created at:', created_at: measurement.created_at },
        { name1: 'Description:', description: measurement.description },
        { name1: 'Speed:', speed: this.speed },
        { name1: 'Current limit:', current_limit: measurement.current_limit },
        {
          name1: 'Connections:',
          connections1: measurement.connection_1,
          connection_2: measurement.connection_2,
          connection_3: measurement.connection_3,
          connection_4: measurement.connection_4,
        },
        { name1: 'Carrier mobility:', mobility: measurement.mobility },
        {
          name1: 'Sheet Resistans:',
          sheet_resistanse: measurement.sheet_resistance,
        },
        { name1: 'Amplitude:', amplitude: measurement.amplitude },
        { name1: 'Angle frequency:', angle_freq: measurement.angle_freq },
        { name1: 'Phase:', phase: measurement.phase },
        { name1: 'Offset', offset: measurement.offset },
      ];
      this.measurementName = measurement.name;
      this.measurement = measurement;
    });
  }

  values: number[];
  ids: number[];

  getrhValues(): void {
    this.backend.get_rh_values_for_measurement(this.id).subscribe((rhValue: PaginatedList<RhValue>) => {
      this.values = rhValue.results.map(v => v.value);
      this.ids = rhValue.results.map(i => i.id);
      this.chartData = [
        { data: this.values, label: 'Graph of measured Rh-values' },
      ];
      this.chartLabels = this.ids;
      let datarhValue = rhValue.results.map(function (obj) {
        return {
          id: obj.id,
          value: obj.value,
        };
      });
      let dataLabels = [
        { name: '', name2: '' },
        { name: 'Measurments Id', name2: 'Rh Values' },
      ];
      this.measurementData = this.measurementData
        .concat(dataLabels)
        .concat(datarhValue);
      this.rhValue = rhValue;
    });
  }

  ngOnInit(): void {
    this.getMeasurement(), this.getrhValues();
  }

  options = {
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

  download_image() {
    var canvas = document.getElementsByTagName('canvas')[0].toDataURL();
    var link = document.createElement('a');
    link.download = this.measurementName;
    link.href = canvas;
    link.click();
  }

  chartOptions = {
    responsive: true,
    scales: {
      yAxes: [
        {
          scaleLabel: {
            display: true,
            labelString: 'Value of Rh',
          },
        },
      ],
      xAxes: [
        {
          scaleLabel: {
            display: true,
            labelString: 'Measurement ID',
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
      pointBackgroundColor: 'rgba(148,159,177,1)',
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: 'rgba(148,159,177,0.8)',
    },
    {
      // dark grey
      backgroundColor: 'rgba(0,0,0,0)',
      borderColor: 'rgba(77,83,96,1)',
      pointBackgroundColor: 'rgba(77,83,96,1)',
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: 'rgba(77,83,96,1)',
    },
  ];

  onChartClick(event) {
    console.log(event);
  }

  results() {
    new ngxCsv(this.measurementData, this.measurementName, this.options);
  }
}