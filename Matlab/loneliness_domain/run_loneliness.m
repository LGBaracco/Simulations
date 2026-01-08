clear all
close all
model = l2('loneliness-l2');
model.simulate(10);
model.plot()
%model.plot('plot_emotion_reg_ability')
