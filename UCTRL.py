from cimpy.cgmes_v2_4_15.ExcitationSystemDynamics import ExcitationSystemDynamics
#all Mohamed

class UCTRL(ExcitationSystemDynamics):


	cgmesProfile = ExcitationSystemDynamics.cgmesProfile

	possibleProfileList = {'class': [cgmesProfile.DY.value, ],
						   'N': [cgmesProfile.DY.value, ],
						   } 

	serializationProfile = {}

	__doc__ += '\n Documentation of parent class ExcitationSystemDynamics: \n' + ExcitationSystemDynamics.__doc__

	def __init__(self, N = "", *args, **kw_args):
		super().__init__(*args, **kw_args)

		self.N = N
		

	def __str__(self):
		str = 'class=UCTRL\n'
		attributes = self.__dict__
		for key in attributes.keys():
			str = str + key + '={}\n'.format(attributes[key])
		return str
