% Tweak this file to open the correct project and display different plots
clear all
close all
model = l2('bystander_effect')
model.reset()
model.simulate(10)
model.plot()