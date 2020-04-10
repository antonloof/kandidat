import { Component, OnInit } from '@angular/core';
import { MatDialogRef } from "@angular/material/dialog";

import { BackendService } from '../backend.service';
import { measure } from '../classes/measure';

interface Speed {
  value: string;
  viewValue: string;
}

@Component({
  selector: 'app-measure-dialog',
  templateUrl: './measure-dialog.component.html',
  styleUrls: ['./measure-dialog.component.css']
})
export class MeasureDialogComponent implements OnInit {
    selectedValue: string;
  error:string;
  
  speed: Speed[] = [
    {value: 'fast-0', viewValue: 'High Speed : Low Resolution'},
    {value: 'medium-1', viewValue: 'Medium Speed : Medium Resolution'},
    {value: 'slow-2', viewValue: 'Low Speed : High Resolution'}
  ];

  submitted = false;
  onSubmit() { this.submitted = true; }


  constructor(
    private backend: BackendService,
    private dialogRef: MatDialogRef<MeasureDialogComponent>,
  ) {  }

  model = new measure(1, '', 5 , "Medium Speed : Medium Resolution", 1 , 2, 3, 4, '');
  
  ngOnInit(): void {
  }

  run(){
    if (this.model.current < 1) {
      window.alert("Target current to low!");
    }
    else if (this.model.current > 10) {
      window.alert("Target current to high!")
    }
    else if( this.model.name == ''){
      window.alert("You must name the measurement!")
    }
    else if (isNaN(this.model.current)) {
      window.alert("The target current must be a number!")
    }
    else {
      this.onSubmit()
      this.dialogRef.close()
      this.backend
      .create_measurement({
        connection_1: this.model.connection_1,
        connection_2: this.model.connection_2,
        connection_3: this.model.connection_3,
        connection_4: this.model.connection_4,
        current_limit: this.model.current,
        name: this.model.name,
        description: this.model.description,
      })

    }
  }
  
  
  cancel(){
     this.submitted = false;
     this.dialogRef.close();
  }
  
 
}
