import { Component, OnInit } from '@angular/core';
import { BackendService } from '../backend.service';
import { measure } from '../classes/mesure';
import { MAT_DIALOG_DATA, MatDialogRef} from "@angular/material/dialog";



@Component({
  selector: 'app-measure-dialog',
  templateUrl: './measure-dialog.component.html',
  styleUrls: ['./measure-dialog.component.css']
})
export class MeasureDialogComponent implements OnInit {
  
  speed = ['High Speed:Low Resulution', 'Medium speed: Medium Resulution', 'Low speed: High Resolution'];

  model = new measure(1, 'name', 0 , this.speed[1]);

  submitted = false;
  onSubmit() { this.submitted = true; }


  constructor(
    private backend: BackendService,
    private dialogRef: MatDialogRef<MeasureDialogComponent>
  ) {  }

  ngOnInit(): void {
  }

  run(){
    // got to home page.. and do measurement.
    this.onSubmit()
    this.dialogRef.close();
  }
  
  
  cancel(){
     // GO HOME and clear. 
     this.submitted = false;
     this.dialogRef.close();
  }
  
 
}
