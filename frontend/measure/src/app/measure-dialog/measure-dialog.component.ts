import { Component, OnInit } from '@angular/core';
import { MatDialogRef } from "@angular/material/dialog";
import {FormControl, Validators, AbstractControl} from '@angular/forms';

import { BackendService } from '../backend.service';
import { CreateMeasurement } from '../classes/measurement';

interface Speed {
  value: number;
  viewValue: string;
}
function currentValidator(control: AbstractControl): { [key: string]: boolean } | null {
  if (control.value < 1e-9 || control.value > 3.3e-3) {
    return { 'current': true };
  }
  return null;
}


@Component({
  selector: 'app-measure-dialog',
  templateUrl: './measure-dialog.component.html',
  styleUrls: ['./measure-dialog.component.css']
})
export class MeasureDialogComponent implements OnInit {
  selectedValue: number;
  error:string;
  nameControl = new FormControl('', [Validators.required]);
  currentControl = new FormControl('', [Validators.required, currentValidator]);

  speeds: Speed[] = [
    {value: 2, viewValue: 'High Speed : Low Resolution'},
    {value: 10, viewValue: 'Medium Speed : Medium Resolution'},
    {value: 20, viewValue: 'Low Speed : High Resolution'}
  ];

  measure: CreateMeasurement = {
    connection_1: 1, 
    connection_2: 2, 
    connection_3: 3, 
    connection_4: 4, 
    current_limit: 1e-6, 
    steps_per_measurement: 10,
    name: 'Name', 
    description:'Description'
  };

  constructor(
    private backend: BackendService,
    private dialogRef: MatDialogRef<MeasureDialogComponent>,
  ) {  }

  submitted = false;
  onSubmit() { this.submitted = true; }

  ngOnInit(): void {
  }

  getNameErrorMessage() {
    if (this.nameControl.hasError('required')) {
      return 'You must name your measurement!';
    }
  }
  getCurrentErrorMessage(){
    if (this.currentControl.hasError('required')){
      return 'You must giva a target current!'
    }
    else if (this.currentControl.hasError('current')){
      return 'Target current must be between 1nA and 3.3mA!'
    }
  }

  run(){
    if(this.nameControl.hasError || this.currentControl.hasError){ }
    else{
      this.onSubmit()
      this.dialogRef.close()
      this.backend
      .create_measurement({
        connection_1: this.measure.connection_1,
        connection_2: this.measure.connection_2,
        connection_3: this.measure.connection_3,
        connection_4: this.measure.connection_4,
        current_limit: this.measure.current_limit,
        steps_per_measurement: this.selectedValue,
        name: this.measure.name,
        description: this.measure.description,
      });  
    }
  }
  
  cancel(){
     this.submitted = false;
     this.dialogRef.close();
  }
  
}


