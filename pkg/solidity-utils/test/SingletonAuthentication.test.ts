import { ethers } from 'hardhat';
import { Contract } from 'ethers';
import { SignerWithAddress } from '@nomiclabs/hardhat-ethers/dist/src/signer-with-address';

import { deploy } from '@balancer-labs/v2-helpers/src/contract';
import Vault from '@balancer-labs/v2-helpers/src/models/vault/Vault';
import { expect } from 'chai';
import { actionId } from '@balancer-labs/v2-helpers/src/models/misc/actions';
import { ANY_ADDRESS } from '@balancer-labs/v2-helpers/src/constants';
import * as expectEvent from '@balancer-labs/v2-helpers/src/test/expectEvent';

describe('SingletonAuthentication', () => {
  let vault: Vault;
  let authorizer: Contract;
  let singleton: Contract;
  let admin: SignerWithAddress, other: SignerWithAddress;

  before('setup signers', async () => {
    [, admin, other] = await ethers.getSigners();
  });

  sharedBeforeEach('deploy authorizer', async () => {
    vault = await Vault.create({ admin });
    if (!vault.authorizer) throw Error('Vault has no Authorizer');
    authorizer = vault.authorizer;
  });

  sharedBeforeEach('deploy singleton', async () => {
    singleton = await deploy('MockSingletonAuthentication', { args: [vault.address] });
  });

  describe('constructor', () => {
    it('sets the vault address', async () => {
      expect(await singleton.getVault()).to.be.eq(vault.address);
    });

    it('uses the authorizer of the vault', async () => {
      expect(await singleton.getAuthorizer()).to.equal(authorizer.address);
    });

    it('tracks authorizer changes in the vault', async () => {
      const action = await actionId(vault.instance, 'setAuthorizer');
      await authorizer.connect(admin).grantPermissions([action], admin.address, [ANY_ADDRESS]);

      await vault.instance.connect(admin).setAuthorizer(other.address);

      expect(await singleton.getAuthorizer()).to.equal(other.address);
    });
  });

  describe('action ids', () => {
    it('are different for each contract', async () => {
      const selector = '0x12345678';
      const otherInstance = await deploy('MockSingletonAuthentication', { args: [vault.address] });
      expect(await singleton.getActionId(selector)).to.not.equal(await otherInstance.getActionId(selector));
    });
  });

  describe('permissioned actions', () => {
    context('when the caller is not authorized', () => {
      it('reverts', async () => {
        await expect(singleton.permissionedAction()).to.be.revertedWith('SENDER_NOT_ALLOWED');
      });
    });

    context('when the caller is authorized', () => {
      sharedBeforeEach('grant permission', async () => {
        await authorizer.grantPermissions(
          [await actionId(singleton, 'permissionedAction')],
          other.address,
          singleton.address
        );
      });

      it('succeeds', async () => {
        const receipt = await (await singleton.connect(other).permissionedAction()).wait();
        expectEvent.inReceipt(receipt, 'ActionExecuted');
      });
    });
  });
});
