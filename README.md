Besides the 3d print, in order to operate this scanner, you'll need a way to run the Python code to send commands to the stepper motors.  The python files are configured to run on a linux machine so you'll need to adjust if you want to run it directly from a Windows PC. 
The project uses two stepper motors although you could eliminate the one that raises and lowers the trash (return) platform and just allow the slides to drop out. <p>
This uses a MKS Gen_L V1.0_008 3D printer board.  I control the camera using the fan switch connected to a relay.  Turning the fan on in the code powers the relay and closing the circuit of the camera trigger wire. 
The code also homes the carrier each time it is run.  The moment switch is connected to one of the Y- pins GND and D14 (be careful not to connect it to the 5v). 



<b> Required items: </b> 
*  Camera (no particular type but some DLSR).
*  A macro lens - I used a Canon 50mm macro f2.5, with a 11mm lens tub extension.  
*  Two small depth stepper motors (NEMA 17 style)
*  RAMPS style motherboard (I used a MKS Gen_L V1.0_008) for controlling the stepper motors and running MARLIN
*  Two stepper drivers (for example A4988)
*  12v relay to trigger the camera. 
*  PC fan to cool the light, although if you used a cooler light you could eliminate this. I just find that halogen lights provide a more complete light spectrum. 
*  12V Halogen light, or another similar light source. 
*  Mirror of approximate 3" x 4" in size - see model file for actual size. 
*  Push button type momemnt switch - used for homing. 
*  Various bearings, 3mm and 5mm rods, belt and pulleys of approximately 11mm and 45mm diameters.
*  Requires some TUP parts, and the model includes compenents which are not printable but were just used for modelling purposes. 


<b> Youtube Video of operation </b> 
https://youtube.com/shorts/vfeZ-w7fXDc?feature=share
