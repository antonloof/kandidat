import { Component, OnInit } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import {
  FormGroup,
  FormBuilder,
  FormControl,
  Validators,
  AbstractControl,
  FormGroupDirective,
  NgForm,
} from '@angular/forms';
import { ErrorStateMatcher } from '@angular/material/core';
import { BackendService } from '../backend.service';

interface Speed {
  value: number;
  viewValue: string;
}

function currentValidator(
  control: AbstractControl
): { [key: string]: boolean } | null {
  if (control.value < 1e-9 || control.value > 3.3e-3) {
    return { current: true };
  }
  return null;
}

class CrossFieldErrorMatcher implements ErrorStateMatcher {
  isErrorState(
    control: FormControl | null,
    form: FormGroupDirective | NgForm | null
  ): boolean {
    return control.dirty && form.invalid;
  }
}

@Component({
  selector: 'app-measure-dialog',
  templateUrl: './measure-dialog.component.html',
  styleUrls: ['./measure-dialog.component.css'],
})
export class MeasureDialogComponent implements OnInit {
  selectedValue: number;
  error: string;
  form: FormGroup;
  connectionForm: FormGroup;
  nameControl = new FormControl('', [Validators.required]);
  currentControl = new FormControl(1e-6, [
    Validators.required,
    currentValidator,
  ]);
  connection1Control = new FormControl(null, [Validators.required]);
  connection2Control = new FormControl(null, [Validators.required]);
  connection3Control = new FormControl(null, [Validators.required]);
  connection4Control = new FormControl(null, [Validators.required]);
  descriptionControl = new FormControl('');
  speedControl = new FormControl(10);
  errorMatcher = new CrossFieldErrorMatcher();
  submitted = false;

  speeds: Speed[] = [
    { value: 20, viewValue: 'High Speed : Low Resolution' },
    { value: 10, viewValue: 'Medium Speed : Medium Resolution' },
    { value: 2, viewValue: 'Low Speed : High Resolution' },
  ];

  constructor(
    private backend: BackendService,
    private dialogRef: MatDialogRef<MeasureDialogComponent>,
    fb: FormBuilder
  ) {
    this.connectionForm = fb.group(
      {
        Con1: this.connection1Control,
        Con2: this.connection2Control,
        Con3: this.connection3Control,
        Con4: this.connection4Control,
      },
      {
        validators: [
          this.conMatchValidator1,
          this.conMatchValidator2,
          this.conMatchValidator3,
          this.conMatchValidator4,
        ],
      }
    );
    this.form = fb.group({
      Speed: this.speedControl,
      Current: this.currentControl,
      Name: this.nameControl,
      Description: this.descriptionControl,
    });
  }
  conMatchValidator1(form: FormGroup) {
    if (
      form.get('Con1').value === form.get('Con2').value ||
      form.get('Con1').value === form.get('Con3').value ||
      form.get('Con1').value === form.get('Con4').value
    ) {
      return { conMatch1: true };
    } else {
      return null;
    }
  }
  conMatchValidator2(form: FormGroup) {
    if (
      form.get('Con2').value === form.get('Con1').value ||
      form.get('Con2').value === form.get('Con3').value ||
      form.get('Con2').value === form.get('Con4').value
    ) {
      return { conMatch2: true };
    } else {
      return null;
    }
  }
  conMatchValidator3(form: FormGroup) {
    if (
      form.get('Con3').value === form.get('Con1').value ||
      form.get('Con3').value === form.get('Con2').value ||
      form.get('Con3').value === form.get('Con4').value
    ) {
      return { conMatch3: true };
    } else {
      return null;
    }
  }
  conMatchValidator4(form: FormGroup) {
    if (
      form.get('Con4').value === form.get('Con1').value ||
      form.get('Con4').value === form.get('Con3').value ||
      form.get('Con4').value === form.get('Con2').value
    ) {
      return { conMatch4: true };
    } else {
      return null;
    }
  }
  ngOnInit(): void {}

  getNameErrorMessage() {
    if (this.nameControl.hasError('required')) {
      return 'You must name your measurement!';
    }
  }
  getCurrentErrorMessage() {
    if (this.currentControl.hasError('required')) {
      return 'You must giva a target current!';
    } else if (this.currentControl.hasError('current')) {
      return 'Target current must be between 1nA and 3.3mA!';
    }
  }
  getConnection1ErrorMessage() {
    if (this.connection1Control.hasError('required')) {
      return 'You must fill in the correct connections!';
    }
  }
  getConnection2ErrorMessage() {
    if (this.connection2Control.hasError('required')) {
      return 'You must fill in the correct connections!';
    }
  }
  getConnection3ErrorMessage() {
    if (this.connection3Control.hasError('required')) {
      return 'You must fill in the correct connections!';
    }
  }
  getConnection4ErrorMessage() {
    if (this.connection4Control.hasError('required')) {
      return 'You must fill in the correct connections!';
    }
  }

  startMeasurement() {
    if (
      !this.nameControl.hasError('required') &&
      !this.currentControl.hasError('required') &&
      !this.currentControl.hasError('current') &&
      !this.form.hasError('conMatch1') &&
      !this.form.hasError('conMatch2') &&
      !this.form.hasError('conMatch3') &&
      !this.form.hasError('conMatch4')
    ) {
      this.dialogRef.close();
      this.backend.create_measurement({
        connection_1: this.connection1Control.value,
        connection_2: this.connection2Control.value,
        connection_3: this.connection3Control.value,
        connection_4: this.connection4Control.value,
        current_limit: this.currentControl.value,
        steps_per_measurement: this.speedControl.value,
        name: this.nameControl.value,
        description: this.descriptionControl.value,
      }).subscribe;
    }
  }
  cancel() {
    this.dialogRef.close();
  }
}
