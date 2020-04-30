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

interface Speed {
  value: number;
  viewValue: string;
}

class CrossFieldErrorMatcher implements ErrorStateMatcher {
  isErrorState(
    control: FormControl | null,
    form: FormGroupDirective | NgForm | null
  ): boolean {
    return (
      control.touched &&
      (form.hasError('duplicate1') ||
        form.hasError('duplicate2') ||
        form.hasError('duplicate3') ||
        form.hasError('duplicate4') ||
        control.invalid)
    );
  }
}

const connectionValidators = [
  Validators.required,
  Validators.min(1),
  Validators.max(32),
];

@Component({
  selector: 'app-measure-dialog',
  templateUrl: './measure-dialog.component.html',
  styleUrls: ['./measure-dialog.component.css'],
})
export class MeasureDialogComponent implements OnInit {
  form: FormGroup;
  nameControl = new FormControl(null, [Validators.required]);
  currentControl = new FormControl(1e-6, [
    Validators.required,
    Validators.min(1e-9),
    Validators.max(3.3e3),
  ]);
  connection1Control = new FormControl(null, connectionValidators);
  connection2Control = new FormControl(null, connectionValidators);
  connection3Control = new FormControl(null, connectionValidators);
  connection4Control = new FormControl(null, connectionValidators);
  connections = [
    { no: 1, control: this.connection1Control },
    { no: 2, control: this.connection2Control },
    { no: 3, control: this.connection3Control },
    { no: 4, control: this.connection4Control },
  ];
  speedControl = new FormControl(10);
  errorStateMatcher = new CrossFieldErrorMatcher();

  speeds: Speed[] = [
    { value: 10, viewValue: 'High Speed : Low Resolution' },
    { value: 5, viewValue: 'Medium Speed : Medium Resolution' },
    { value: 3, viewValue: 'Low Speed : High Resolution' },
  ];

  constructor(
    private dialogRef: MatDialogRef<MeasureDialogComponent>,
    private fb: FormBuilder
  ) {}

  ngOnInit(): void {
    this.form = this.fb.group(
      {
        Speed: this.speedControl,
        Current: this.currentControl,
        Name: this.nameControl,
        Con1: this.connection1Control,
        Con2: this.connection2Control,
        Con3: this.connection3Control,
        Con4: this.connection4Control,
      },
      {
        validators: [this.connectionDuplicateValidator],
      }
    );
    this.form.controls['Speed'].setValue(10, { onlySelf: true });
  }

  connectionDuplicateValidator(form: FormGroup) {
    const values = [1, 2, 3, 4].map(i => form.get('Con' + i).value);
    const duplicatesIndexes = values
      .map((v, i) => [i, values.indexOf(v), values.lastIndexOf(v), v])
      .filter(t => t[0] != t[1] || t[0] != t[2])
      .filter(t => !!t[3])
      .map(t => t[0]);
    if (duplicatesIndexes.length) {
      const ret = {};
      duplicatesIndexes.forEach(i => {
        ret['duplicate' + (i + 1)] = true;
      });
      return ret;
    }
    return null;
  }

  getMeasurement() {
    return {
      connection_1: this.connection1Control.value,
      connection_2: this.connection2Control.value,
      connection_3: this.connection3Control.value,
      connection_4: this.connection4Control.value,
      current_limit: this.currentControl.value,
      steps_per_measurement: this.speedControl.value,
      name: this.nameControl.value,
    };
  }

  startMeasurement() {
    if (this.form.valid) {
      this.dialogRef.close(this.getMeasurement());
    }
  }

  cancel() {
    this.dialogRef.close();
  }
}
